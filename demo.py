from src.pipline.training_pipeline import TrainingPipeline

obj = TrainingPipeline()
obj.run_pipeline()
# import os
# print(os.getenv("mongoDB_url"))
# import numpy as np

# X = np.array([
#     [1, 2],
#     [3, 4],
#     [5, 6]
# ])

# y = [0, 1, 0]

# result = np.hstack((X, np.array(y).reshape(-1, 1)))

# print(result)
# print(result.shape)

