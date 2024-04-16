IDS_SEPARATOR=':'

defcombine_ids(ms_id,ms_uid):
    ifnotms_id:
        returnFalse
    returnms_id+IDS_SEPARATOR+(ms_uidifms_uidelse'')

defsplit_ids(value):
    ids=value.split(IDS_SEPARATOR)
    returntuple(ids)iflen(ids)>1andids[1]else(ids[0],False)
