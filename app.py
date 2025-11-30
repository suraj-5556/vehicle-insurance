from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run
import asyncio
import logging
from typing import Optional
from queue import Queue
import threading

# Importing constants and pipeline modules from the project
from src.constants import APP_HOST, APP_PORT
from src.pipline.prediction_pipeline import VehicleData, VehicleDataClassifier
from src.pipline.training_pipeline import TrainingPipeline
from src.logger import logging as custom_logger  # Your custom logger module

# Initialize FastAPI application
app = FastAPI()

# Mount the 'static' directory for serving static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 template engine for rendering HTML templates
templates = Jinja2Templates(directory='templates')

# Allow all origins for Cross-Origin Resource Sharing (CORS)
origins = ["*"]

# Configure middleware to handle CORS, allowing requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueueHandler(logging.Handler):
    """
    Custom logging handler that puts log records into a queue.
    This allows real-time log streaming to the frontend.
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)


class DataForm:
    """
    DataForm class to handle and process incoming form data.
    This class defines the vehicle-related attributes expected from the form.
    """
    def __init__(self, request: Request):
        self.request: Request = request
        self.Gender: Optional[int] = None
        self.Age: Optional[int] = None
        self.Driving_License: Optional[int] = None
        self.Region_Code: Optional[float] = None
        self.Previously_Insured: Optional[int] = None
        self.Annual_Premium: Optional[float] = None
        self.Policy_Sales_Channel: Optional[float] = None
        self.Vintage: Optional[int] = None
        self.Vehicle_Age_lt_1_Year: Optional[int] = None
        self.Vehicle_Age_gt_2_Years: Optional[int] = None
        self.Vehicle_Damage_Yes: Optional[int] = None
                
    async def get_vehicle_data(self):
        """
        Method to retrieve and assign form data to class attributes.
        This method is asynchronous to handle form data fetching without blocking.
        """
        form = await self.request.form()
        self.Gender = form.get("Gender")
        self.Age = form.get("Age")
        self.Driving_License = form.get("Driving_License")
        self.Region_Code = form.get("Region_Code")
        self.Previously_Insured = form.get("Previously_Insured")
        self.Annual_Premium = form.get("Annual_Premium")
        self.Policy_Sales_Channel = form.get("Policy_Sales_Channel")
        self.Vintage = form.get("Vintage")
        self.Vehicle_Age_lt_1_Year = form.get("Vehicle_Age_lt_1_Year")
        self.Vehicle_Age_gt_2_Years = form.get("Vehicle_Age_gt_2_Years")
        self.Vehicle_Damage_Yes = form.get("Vehicle_Damage_Yes")


# Route to render the main page with the form
@app.get("/", tags=["authentication"])
async def index(request: Request):
    """
    Renders the main HTML form page for vehicle data input.
    """
    return templates.TemplateResponse(
            "vehicledata.html",{"request": request, "context": "Rendering"})


# SSE endpoint for training with real-time logs from custom logger
@app.get("/train-stream")
async def train_stream():
    """
    Endpoint to stream training logs in real-time using Server-Sent Events.
    Integrates with your custom src.logger.logging module.
    """
    async def event_generator():
        log_queue = Queue()
        queue_handler = QueueHandler(log_queue)
        
        # Set formatter for the queue handler
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        queue_handler.setFormatter(formatter)
        
        # Get the root logger (or your specific logger if you have a named one)
        logger = logging.getLogger()
        original_level = logger.level
        logger.setLevel(logging.INFO)
        logger.addHandler(queue_handler)
        
        try:
            yield f"data: 🚀 Initializing training pipeline...\n\n"
            await asyncio.sleep(0.1)
            
            # Run training in a separate thread to avoid blocking
            def run_training():
                try:
                    train_pipeline = TrainingPipeline()
                    train_pipeline.run_pipeline()
                    log_queue.put("TRAINING_COMPLETE")
                except Exception as e:
                    log_queue.put(f"ERROR: {str(e)}")
                    log_queue.put("TRAINING_COMPLETE")
            
            training_thread = threading.Thread(target=run_training)
            training_thread.start()
            
            # Stream logs from the queue
            while True:
                if not log_queue.empty():
                    log_message = log_queue.get()
                    
                    if log_message == "TRAINING_COMPLETE":
                        yield f"data: ✓ Training pipeline completed successfully!\n\n"
                        yield f"data: DONE\n\n"
                        break
                    
                    # Format the message for frontend
                    yield f"data: {log_message}\n\n"
                else:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
            
            # Wait for training thread to complete
            training_thread.join(timeout=1)
            
        except Exception as e:
            yield f"data: ❌ ERROR: {str(e)}\n\n"
            yield f"data: DONE\n\n"
        finally:
            # Clean up: remove the queue handler
            logger.removeHandler(queue_handler)
            logger.setLevel(original_level)
    
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# Route to trigger the model training process (fallback)
@app.get("/train")
async def trainRouteClient():
    """
    Endpoint to initiate the model training pipeline (fallback).
    """
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!!!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")


# Route to handle form submission and make predictions
@app.post("/")
async def predictRouteClient(request: Request):
    """
    Endpoint to receive form data, process it, and make a prediction.
    """
    try:
        form = DataForm(request)
        await form.get_vehicle_data()
        
        vehicle_data = VehicleData(
                                Gender= form.Gender,
                                Age = form.Age,
                                Driving_License = form.Driving_License,
                                Region_Code = form.Region_Code,
                                Previously_Insured = form.Previously_Insured,
                                Annual_Premium = form.Annual_Premium,
                                Policy_Sales_Channel = form.Policy_Sales_Channel,
                                Vintage = form.Vintage,
                                Vehicle_Age_lt_1_Year = form.Vehicle_Age_lt_1_Year,
                                Vehicle_Age_gt_2_Years = form.Vehicle_Age_gt_2_Years,
                                Vehicle_Damage_Yes = form.Vehicle_Damage_Yes
                                )

        # Convert form data into a DataFrame for the model
        vehicle_df = vehicle_data.get_vehicle_input_data_frame()

        # Initialize the prediction pipeline
        model_predictor = VehicleDataClassifier()

        # Make a prediction and retrieve the result
        value = model_predictor.predict(dataframe=vehicle_df)[0]

        # Interpret the prediction result as 'Response-Yes' or 'Response-No'
        status = "Response-Yes" if value == 1 else "Response-No"

        # Render the same HTML page with the prediction result
        return templates.TemplateResponse(
            "vehicledata.html",
            {"request": request, "context": status},
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}


# Main entry point to start the FastAPI server
if __name__ == "__main__":
    app_run(app)
