from typing import Union,Literal
from datetime import datetime
from skynamo.models.Address import Address
from skynamo.shared.helpers import getDateTimeObjectFromSkynamoDateTimeStr
from skynamo.models.CustomFormBase import CustomFormBase

class CustomForm(CustomFormBase):
	def __init__(self,json:dict):
		super().__init__(json)
