from ..shared.helpers import getStringWithOnlyValidPythonVariableCharacters
class CustomFieldArg:
	def __init__(self,customField:dict,formPrefix:str):
		customFieldType=customField['type']
		customFieldId=customField['id']
		customFieldName=getStringWithOnlyValidPythonVariableCharacters(customField['name'])
		customPropName=f'{formPrefix}c{customFieldId}_{customFieldName}'
		argType='str'
		if customFieldType=='Text Field':
			argType='str'
		elif customFieldType=='Number Field':
			argType='float'
		elif customFieldType=='Date Time Field':
			argType='datetime'
		elif customFieldType=='Single Value Enumeration Field':
			commaSeparatedOptions=__getCommaSeperatedEnums(customField['enumeration_values'])
			argType=f'Literal["{commaSeparatedOptions}"]'
		elif customFieldType=='Multi Value Enumeration Field':
			commaSeparatedOptions=__getCommaSeperatedEnums(customField['enumeration_values'])
			argType=f'list[Literal["{commaSeparatedOptions}"]]'
		elif customFieldType=='Single Value Hierarchical Enumeration Field':
			commaSeparatedOptions=__getCommaSeperatedEnumsForNestedEnums(customField['enumeration_values'])
			argType=f'Literal["{commaSeparatedOptions}"]'
		elif customFieldType=='Multi Value Hierarchical Enumeration Field':
			commaSeparatedOptions=__getCommaSeperatedEnumsForNestedEnums(customField['enumeration_values'])
			argType=f'list[Literal["{commaSeparatedOptions}"]]'
		elif customFieldType=='Address Field':
			argType='Address'
		elif customFieldType=='Single Value Lookup Entity Field':
			argType='int'
		elif customFieldType=='Multi Value Lookup Entity Field':
			argType='list[int]'
		self.argType:str=argType
		self.argName:str=customPropName
		self.required:bool=customField['required']

def __getFormPrefix(formDef):
	formType=formDef['type']
	formPrefix=''
	formId=formDef['id']
	if formType in ['Order','CreditRequest','Quote']:
		formPrefix=f'f{formId}_'
	return formPrefix

def __getCommaSeperatedEnums(enumerationValues:list[dict]):
	commaSeparatedOptions=''
	for enum in enumerationValues:
		commaSeparatedOptions+=f'{enum["label"]},'
	return commaSeparatedOptions[:-1]

def __getCommaSeperatedEnumsForNestedEnums(enumValues:list[dict]):
	commaSeparatedOptions=''
	parentToChildEnumValues={}
	for enum in enumValues:
		if 'parent_id' not in enum:
			parentToChildEnumValues[enum['id']]={'label':enum['label'],'children':[]}
		else:
			parentToChildEnumValues[enum['parent_id']]['children'].append(enum)
	for parentEnumId in parentToChildEnumValues:
		for childEnum in parentToChildEnumValues[parentEnumId]['children']:
			commaSeparatedOptions+=f'{parentToChildEnumValues[parentEnumId]["label"]} - {childEnum["label"]},'
	return commaSeparatedOptions[:-1]

def getListCustomFieldArgs(formDef):
	customFields=formDef['custom_fields']
	skippedCustomFieldTypes=['Images Field','Signature Field','Sketch Field','Divider Field','Label Field']
	listOfCustomFieldArgs:list[CustomFieldArg]=[]
	formPrefix=__getFormPrefix(formDef)
	for customField in customFields:
		customFieldType=customField['type']
		if customFieldType in skippedCustomFieldTypes:
			continue
		listOfCustomFieldArgs.append(CustomFieldArg(customField,formPrefix))
	return listOfCustomFieldArgs