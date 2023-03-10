from .WriteOperationCls import WriteOperation
from .writeHelpers import getWriteOperationToUpdateObject,getBodyForWriteOperation,addWarehouseAndLabelToStockLevelUpdateIfPresent
from .execute import executeWrites
from typing import Union,Literal,Union
from ..models.Invoice import Invoice
from ..models.InvoiceItem import InvoiceItem
from datetime import datetime
from typing import List
from ..models.CustomFieldsToCreate import CustomFieldsToCreate


class WriterBase:
	def __init__(self):
		self.writeOperations:List[WriteOperation]=[]
	def apply(self):
		res= executeWrites(self.writeOperations)
		self.writeOperations=[]
		return res
	##unchanging update operations
	def addStockLevelUpdate(self,product_id:int,order_unit_id:int,level:int,warehouse_id:int=0,label:Union[None,str]=None):
		item={'product_id': product_id, 'order_unit_id': order_unit_id, 'level': level}
		addWarehouseAndLabelToStockLevelUpdateIfPresent(item,warehouse_id,label)
		self.writeOperations.append(WriteOperation("stocklevels", "post", item))

	def addStockLevelUpdateUsingProductCodeAndUnitName(self,product_code:str,order_unit_name:str,level:int,warehouse_id:int=0,label:Union[None,str]=None):
		item={'product_code': product_code, 'order_unit_name': order_unit_name, 'level': level}
		addWarehouseAndLabelToStockLevelUpdateIfPresent(item,warehouse_id,label)
		self.writeOperations.append(WriteOperation("stocklevels", "post", item))

	def addPriceUpdate(self,product_id:int,order_unit_id:int,price:float,price_list_id:int,tax_rate_id:Union[None,int]=None):
		item= {'product_id': product_id, 'order_unit_id': order_unit_id, 'price': price, 'price_list_id': price_list_id}
		if tax_rate_id!=None:
			item['tax_rate_id']=tax_rate_id
		self.writeOperations.append(WriteOperation("prices", "post",item))

	def addPriceUpdateUsingProductCodeAndUnitName(self,product_code:str,order_unit_name:str,price:float,price_list_id:int,tax_rate_id:Union[None,int]=None):
		item= {'product_code': product_code, 'order_unit_name': order_unit_name, 'price': price, 'price_list_id': price_list_id}
		if tax_rate_id!=None:
			item['tax_rate_id']=tax_rate_id
		self.writeOperations.append(WriteOperation("prices", "post",item))

	def addInvoiceUpdate(self,invoice:Invoice,fieldsToUpdate:List[str]):
		self.writeOperations.append(getWriteOperationToUpdateObject(invoice,fieldsToUpdate))
	##unchanging create operations
	def addInvoiceCreate(self,date:datetime,customer_code:str,items:List[InvoiceItem],reference='',status:Union[None,Literal['Draft','Authorized','Delivered','Outstanding','Paid','Deleted']]=None,due_date:Union[None,datetime]=None,taxIsIncludedInLineValues=True,outstanding_balance:Union[None,float]=None):
		body=getBodyForWriteOperation(locals())
		del body['taxIsIncludedInLineValues']
		if not(taxIsIncludedInLineValues):
			for item in body['items']:
				taxAmount=0
				if 'tax_amount' in item:
					taxAmount=item['tax_amount']
				item['value']=item['value']+taxAmount
		self.writeOperations.append(WriteOperation("invoices", "post", body))

	def addScheduledVisitCreate(self,assigned_user_name:str,customer_code:str,due_date:datetime,end_time:Union[datetime,None]=None,comment:Union[None,str]=None):
		body=getBodyForWriteOperation(locals())
		if end_time==None:
			body['all_day']=True
		self.writeOperations.append(WriteOperation("scheduledvisits", "post", body))

	def addCustomFieldCreations(self,customFieldsToCreate:CustomFieldsToCreate):
		self.writeOperations.append(WriteOperation("integrations", "post", {'action':'AddCustomFields','fields_to_add':customFieldsToCreate.fields_to_add},canBeCombinedWithOtherWritesInAList=False))