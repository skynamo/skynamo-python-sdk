from .WriteOperationCls import WriteOperation
from .WriteErrorCls import WriteError
from ..shared.api import makeRequest
import math,threading
from typing import List

def executeWrites(writeOperations:List[WriteOperation]):
	writeBatchesGroupedByDataTypeAndHttpMethod=[]
	for write in writeOperations:
		found=False
		for writeBatch in writeBatchesGroupedByDataTypeAndHttpMethod:
			if writeBatch[0].dataType==write.dataType and writeBatch[0].httpMethod==write.httpMethod:
				writeBatch.append(write)
				found=True
				break
		if not found:
			writeBatchesGroupedByDataTypeAndHttpMethod.append([write])
	subBatchesWithMaxSizeOf20:List[List[WriteOperation]]=[]
	for writeBatch in writeBatchesGroupedByDataTypeAndHttpMethod:
		for i in range(math.ceil(len(writeBatch)/20)):
			subBatchesWithMaxSizeOf20.append(writeBatch[i*20:i*20+20])
	return __makeThreadedWrites(subBatchesWithMaxSizeOf20)

def __makeThreadedWrites(subBatchesWithMaxSizeOf20:List[List[WriteOperation]]):
	threads=[]
	errors:List[WriteError]=[]
	for subBatch in subBatchesWithMaxSizeOf20:
		threads.append(threading.Thread(target=__makeWriteRequest,args=(subBatch,errors)))
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	return errors

def __makeWriteRequest(writeOperations:List[WriteOperation],errors:List[WriteError]):
	writeItems=[]
	for write in writeOperations:
		writeItems.append(write.itemOrId)
	results=makeRequest(writeOperations[0].httpMethod,writeOperations[0].dataType,writeItems)#type:ignore
	if 'errors' in results:
		for error in results['errors']:
			errors.append(WriteError(writeOperations[0].dataType,writeOperations[0].httpMethod,writeItems[error['index']],error['detail'])) #type:ignore