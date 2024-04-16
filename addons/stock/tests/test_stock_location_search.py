#-*-coding:utf-8-*-

fromflectra.testsimportcommon


classTestStockLocationSearch(common.TransactionCase):
    defsetUp(self):
        super(TestStockLocationSearch,self).setUp()
        self.location=self.env['stock.location']
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.sublocation=self.env['stock.location'].create({
            'name':'Shelf2',
            'barcode':1201985,
            'location_id':self.stock_location.id
        })
        self.location_barcode_id=self.sublocation.id
        self.barcode=self.sublocation.barcode
        self.name=self.sublocation.name

    deftest_10_location_search_by_barcode(self):
        """Searchstocklocationbybarcode"""
        location_names=self.location.name_search(name=self.barcode)
        self.assertEqual(len(location_names),1)
        location_id_found=location_names[0][0]
        self.assertEqual(self.location_barcode_id,location_id_found)

    deftest_20_location_search_by_name(self):
        """Searchstocklocationbyname"""
        location_names=self.location.name_search(name=self.name)
        location_ids_found=[location_name[0]forlocation_nameinlocation_names]
        self.assertTrue(self.location_barcode_idinlocation_ids_found)

    deftest_30_location_search_wo_results(self):
        """Searchstocklocationwithoutresults"""
        location_names=self.location.name_search(name='nonexistent')
        self.assertFalse(location_names)
