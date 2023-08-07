import sys
from omegaconf import DictConfig, OmegaConf, open_dict

from sklearn.model_selection import StratifiedKFold, KFold
from torch.utils.data import WeightedRandomSampler
from pathlib import Path
import pandas as pd

import numpy as np
from collections import Counter
import torch
from typing import Callable, Tuple, Union
from dataclasses import dataclass
import os
from hydra.core.hydra_config import HydraConfig
from hydra.utils import instantiate
from pytorch_lightning import seed_everything
import hydra
from flash.image import ImageClassificationData, ImageClassifier
from flash.core.data.io.input_transform import InputTransform
from flash.core.data.io.input import DataKeys
from flash.core.data.transforms import ApplyToKeys
from flash.core.data.utils import download_data
import flash
from torchvision import transforms as T

from onnxruntime.quantization import CalibrationDataReader
import torch
from torch.utils.data import Dataset
from flash.core.data.io.input import DataKeys
import onnxoptimizer

import onnxruntime
from onnxruntime.quantization.shape_inference import quant_pre_process
from onnxruntime.quantization import QuantFormat, QuantType, quantize_static

from pytorch_quantization import nn as quant_nn


#OBJECT DETECTION
from icevision.tfms import A
import albumentations as alb
import kornia.geometry as Kg
import kornia.augmentation as Ka
from flash.image import ObjectDetectionData, ObjectDetector
from flash.image import ImageClassificationData, ImageClassifier
from flash.core.data.transforms import ApplyToKeys
from flash.core.data.io.input import DataKeys
from flash.core.data.utils import download_data

#ANOMALY DETECTION
import einops
from pytorch_lightning.callbacks import EarlyStopping
from pytorch_lightning.utilities.types import STEP_OUTPUT
from FrEIA.framework import SequenceINN
from FrEIA.modules import AllInOneBlock

from skimage import morphology
from albumentations.pytorch import ToTensorV2


import mlflow
import captum

# from aimet_torch.compress import ModelCompressor


# import fiftyone as fo
# from fiftyone.core.view import DatasetView
# from fiftyone import ViewField as F