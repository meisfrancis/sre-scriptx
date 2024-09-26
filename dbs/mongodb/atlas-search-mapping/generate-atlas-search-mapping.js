require('ts-node').register();

const data = require(process.argv[2]);
const targetSchema = process.argv[3]
const STR = 'SchemaString';
const BOOL = 'SchemaBoolean';
const NUM = 'SchemaNumber';
const DATE = 'SchemaDate';
const OID = 'ObjectId';
const MX = 'Mixed';
const ARRAY = 'SchemaArray';
const EM_DOC = 'DocumentArrayPath';
const DOC = 'SubdocumentPath';
const getClassName = (instance) => instance.constructor.name;
const getSchemaArrayItemClassName = (instance) => instance.caster.constructor.name;
const ATLAS_SEARCH_MAP = {
  string: [{type: 'string'}, {type: 'token', normalizer: 'lowercase'}],
  number: [{type: 'number'}],
  boolean: [{type: 'boolean'}],
  date: [{type: 'date'}],
  objectId: [{type: 'objectId'}],
  mixed: [{type: 'string'}, {
    type: 'token',
    normalizer: 'lowercase',
  }, {type: 'number'}, {type: 'boolean'}, {type: 'date'}, {type: 'objectId'}],
  stringArr: [{type: 'string'}],
};
const COMMON_CASES = [STR, BOOL, NUM, DATE, OID, MX]
const ADV_CASES = [DOC, EM_DOC]
const COMMON_CASE_MAP = {}
COMMON_CASE_MAP[STR] = ATLAS_SEARCH_MAP.string
COMMON_CASE_MAP[BOOL] = ATLAS_SEARCH_MAP.boolean
COMMON_CASE_MAP[NUM] = ATLAS_SEARCH_MAP.number
COMMON_CASE_MAP[DATE] = ATLAS_SEARCH_MAP.date
COMMON_CASE_MAP[OID] = ATLAS_SEARCH_MAP.objectId
COMMON_CASE_MAP[MX] = ATLAS_SEARCH_MAP.mixed
const ADV_CASE_MAP = {}
ADV_CASE_MAP[DOC] = 'document'
ADV_CASE_MAP[EM_DOC] = 'embeddedDocuments'
const root = {
  mappings: {
    dynamic: false,
    fields: {}
  }
}
const scanAndGenerate = (mapping, schema) => {
  for (const [k, v] of Object.entries(schema.paths)) {
    const clsName = getClassName(v)
    if (COMMON_CASES.includes(clsName)) {
      mapping[k] = COMMON_CASE_MAP[clsName]
    } else if (clsName === ARRAY) {
      const arrItemClsName = getSchemaArrayItemClassName(v)
      if (arrItemClsName === STR) mapping[k] = ATLAS_SEARCH_MAP.stringArr
      else mapping[k] = COMMON_CASE_MAP[arrItemClsName]
    } else if (ADV_CASES.includes(clsName)) {
      mapping[k] = {
        type: ADV_CASE_MAP[clsName],
        dynamic: false,
        fields: {}
      }
      scanAndGenerate(mapping[k].fields, v.schema)
    } else {
      mapping[k] = `UNDEFINED: ${clsName}`
    }
  }
}

scanAndGenerate(root.mappings.fields, data[targetSchema])

require('fs').writeFileSync('atlas-search-mapping.json', JSON.stringify(root))

