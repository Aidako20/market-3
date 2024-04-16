#-*-coding:utf-8-*-

importjson

fromflectraimportfields


defmonkey_patch(cls):
    """Returnamethoddecoratortomonkey-patchthegivenclass."""
    defdecorate(func):
        name=func.__name__
        func.super=getattr(cls,name,None)
        setattr(cls,name,func)
        returnfunc
    returndecorate


#
#Implementsparsefieldsbymonkey-patchingfields.Field
#

fields.Field.__doc__+="""

        .._field-sparse:

        ..rubric::Sparsefields

        Sparsefieldshaveaverysmallprobabilityofbeingnotnull.Therefore
        manysuchfieldscanbeserializedcompactlyintoacommonlocation,the
        latterbeingaso-called"serialized"field.

        :paramsparse:thenameofthefieldwherethevalueofthisfieldmust
            bestored.
"""
fields.Field.sparse=None

@monkey_patch(fields.Field)
def_get_attrs(self,model,name):
    attrs=_get_attrs.super(self,model,name)
    ifattrs.get('sparse'):
        #bydefault,sparsefieldsarenotstoredandnotcopied
        attrs['store']=False
        attrs['copy']=attrs.get('copy',False)
        attrs['compute']=self._compute_sparse
        ifnotattrs.get('readonly'):
            attrs['inverse']=self._inverse_sparse
    returnattrs

@monkey_patch(fields.Field)
def_compute_sparse(self,records):
    forrecordinrecords:
        values=record[self.sparse]
        record[self.name]=values.get(self.name)
    ifself.relational:
        forrecordinrecords:
            record[self.name]=record[self.name].exists()

@monkey_patch(fields.Field)
def_inverse_sparse(self,records):
    forrecordinrecords:
        values=record[self.sparse]
        value=self.convert_to_read(record[self.name],record,use_name_get=False)
        ifvalue:
            ifvalues.get(self.name)!=value:
                values[self.name]=value
                record[self.sparse]=values
        else:
            ifself.nameinvalues:
                values.pop(self.name)
                record[self.sparse]=values


#
#Definitionandimplementationofserializedfields
#

classSerialized(fields.Field):
    """Serializedfieldsprovidethestorageforsparsefields."""
    type='serialized'
    column_type=('text','text')

    prefetch=False                   #notprefetchedbydefault

    defconvert_to_column(self,value,record,values=None,validate=True):
        returnself.convert_to_cache(value,record,validate=validate)

    defconvert_to_cache(self,value,record,validate=True):
        #cacheformat:json.dumps(value)orNone
        returnjson.dumps(value)ifisinstance(value,dict)else(valueorNone)

    defconvert_to_record(self,value,record):
        returnjson.loads(valueor"{}")


fields.Serialized=Serialized
