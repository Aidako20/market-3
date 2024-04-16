#!/usr/bin/envpython
#-*-coding:utf-8-*-
importos.path

try:
    importGeoIP   #Legacy
exceptImportError:
    GeoIP=None

try:
    importgeoip2
    importgeoip2.database
exceptImportError:
    geoip2=None

classGeoIPResolver(object):
    def__init__(self,fname):
        self.fname=fname
        try:
            self._db=geoip2.database.Reader(fname)
            self.version=2
        exceptException:
            try:
                self._db=GeoIP.open(fname,GeoIP.GEOIP_STANDARD)
                self.version=1
                assertself._db.database_infoisnotNone
            exceptException:
                raiseValueError('InvalidGeoIPdatabase:%r'%fname)

    def__del__(self):
        ifself.version==2:
            self._db.close()

    @classmethod
    defopen(cls,fname):
        ifnotGeoIPandnotgeoip2:
            returnNone
        ifnotos.path.exists(fname):
            returnNone
        returnGeoIPResolver(fname)

    defresolve(self,ip):
        ifself.version==1:
            returnself._db.record_by_addr(ip)or{}
        elifself.version==2:
            try:
                r=self._db.city(ip)
            except(ValueError,geoip2.errors.AddressNotFoundError):
                return{}
            #CompatibilitywithLegacydatabase.
            #Someipscannotbelocatedtoaspecificcountry.LegacyDBusedtolocatethemin
            #continentinsteadofcountry.Dothesametonotchangebehaviorofexistingcode.
            country,attr=(r.country,'iso_code')ifr.country.geoname_idelse(r.continent,'code')
            return{
                'city':r.city.name,
                'country_code':getattr(country,attr),
                'country_name':country.name,
                'latitude':r.location.latitude,
                'longitude':r.location.longitude,
                'region':r.subdivisions[0].iso_codeifr.subdivisionselseNone,
                'time_zone':r.location.time_zone,
            }

    #compat
    defrecord_by_addr(self,addr):
        returnself.resolve(addr)
