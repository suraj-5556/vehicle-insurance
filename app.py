from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from uvicorn import run as app_run
import asyncio
import logging
from typing import Optional
from queue import Queue
import threading
import json

# Importing constants and pipeline modules from the project
from src.constants import APP_HOST, APP_PORT
from src.pipline.prediction_pipeline import VehicleData, VehicleDataClassifier
from src.pipline.training_pipeline import TrainingPipeline
from src.logger import logging as custom_logger

# Initialize FastAPI application
app = FastAPI()

# Mount the 'static' directory for serving static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 template engine
templates = Jinja2Templates(directory='templates')

# CORS configuration
origins = ["*"]

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
        """
        form = await self.request.form()
        self.Gender = int(form.get("Gender"))
        self.Age = int(form.get("Age"))
        self.Driving_License = int(form.get("Driving_License"))
        self.Region_Code = float(form.get("Region_Code"))
        self.Previously_Insured = int(form.get("Previously_Insured"))
        self.Annual_Premium = float(form.get("Annual_Premium"))
        self.Policy_Sales_Channel = float(form.get("Policy_Sales_Channel"))
        self.Vintage = int(form.get("Vintage"))
        self.Vehicle_Age_lt_1_Year = int(form.get("Vehicle_Age_lt_1_Year"))
        self.Vehicle_Age_gt_2_Years = int(form.get("Vehicle_Age_gt_2_Years"))
        self.Vehicle_Damage_Yes = int(form.get("Vehicle_Damage_Yes"))


# Route to render the main page
@app.get("/", tags=["authentication"])
async def index(request: Request):
    """
    Renders the main HTML form page for vehicle insurance prediction.
    """
    return templates.TemplateResponse(
            "vehicledata.html",{"request": request})


# SSE endpoint for training with real-time logs
@app.get("/train-stream")
async def train_stream():
    """
    Endpoint to stream training logs in real-time using Server-Sent Events.
    """
    async def event_generator():
        log_queue = Queue()
        queue_handler = QueueHandler(log_queue)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        queue_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        original_level = logger.level
        logger.setLevel(logging.INFO)
        logger.addHandler(queue_handler)
        
        try:
            yield f"data: 🚀 Initializing training pipeline...\n\n"
            await asyncio.sleep(0.1)
            
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
            
            while True:
                if not log_queue.empty():
                    log_message = log_queue.get()
                    
                    if log_message == "TRAINING_COMPLETE":
                        yield f"data: ✓ Training pipeline completed successfully!\n\n"
                        yield f"data: DONE\n\n"
                        break
                    
                    yield f"data: {log_message}\n\n"
                else:
                    await asyncio.sleep(0.1)
            
            training_thread.join(timeout=1)
            
        except Exception as e:
            yield f"data: ❌ ERROR: {str(e)}\n\n"
            yield f"data: DONE\n\n"
        finally:
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


# SSE endpoint for prediction with real-time logs
@app.get("/predict-stream")
async def predict_stream(
    Gender: int,
    Age: int,
    Driving_License: int,
    Region_Code: float,
    Previously_Insured: int,
    Annual_Premium: float,
    Policy_Sales_Channel: float,
    Vintage: int,
    Vehicle_Age_lt_1_Year: int,
    Vehicle_Age_gt_2_Years: int,
    Vehicle_Damage_Yes: int
):
    """
    Endpoint to stream prediction logs in real-time using Server-Sent Events.
    """
    async def event_generator():
        log_queue = Queue()
        queue_handler = QueueHandler(log_queue)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        queue_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        original_level = logger.level
        logger.setLevel(logging.INFO)
        logger.addHandler(queue_handler)
        
        try:
            yield f"data: 🔍 Starting prediction process...\n\n"
            await asyncio.sleep(0.1)
            
            result = {"status": False, "prediction": None, "risk_level": None}
            
            def run_prediction():
                try:
                    vehicle_data = VehicleData(
                        Gender=Gender,
                        Age=Age,
                        Driving_License=Driving_License,
                        Region_Code=Region_Code,
                        Previously_Insured=Previously_Insured,
                        Annual_Premium=Annual_Premium,
                        Policy_Sales_Channel=Policy_Sales_Channel,
                        Vintage=Vintage,
                        Vehicle_Age_lt_1_Year=Vehicle_Age_lt_1_Year,
                        Vehicle_Age_gt_2_Years=Vehicle_Age_gt_2_Years,
                        Vehicle_Damage_Yes=Vehicle_Damage_Yes
                    )
                    
                    vehicle_df = vehicle_data.get_vehicle_input_data_frame()
                    model_predictor = VehicleDataClassifier()
                    value = model_predictor.predict(dataframe=vehicle_df)[0]
                    
                    result["status"] = True
                    result["prediction"] = int(value)
                    
                    # Determine risk level based on features
                    if value == 1:
                        if Previously_Insured == 0 and Vehicle_Damage_Yes == 1:
                            result["risk_level"] = "High"
                        elif Vehicle_Damage_Yes == 1:
                            result["risk_level"] = "Medium"
                        else:
                            result["risk_level"] = "Low"
                    else:
                        result["risk_level"] = "Low"
                    
                    log_queue.put("PREDICTION_COMPLETE")
                except Exception as e:
                    log_queue.put(f"ERROR: {str(e)}")
                    log_queue.put("PREDICTION_COMPLETE")
            
            prediction_thread = threading.Thread(target=run_prediction)
            prediction_thread.start()
            
            while True:
                if not log_queue.empty():
                    log_message = log_queue.get()
                    
                    if log_message == "PREDICTION_COMPLETE":
                        yield f"data: ✓ Prediction completed successfully!\n\n"
                        yield f"data: RESULT:{json.dumps(result)}\n\n"
                        yield f"data: DONE\n\n"
                        break
                    
                    yield f"data: {log_message}\n\n"
                else:
                    await asyncio.sleep(0.1)
            
            prediction_thread.join(timeout=1)
            
        except Exception as e:
            yield f"data: ❌ ERROR: {str(e)}\n\n"
            yield f"data: DONE\n\n"
        finally:
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


# Main entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

