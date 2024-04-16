flectra.define('google_drive.gdrive_integration',function(require){
    "usestrict";

    constFormView=require('web.FormView');
    consttestUtils=require('web.test_utils');

    constcpHelpers=testUtils.controlPanel;

    QUnit.module('GoogleDriveIntegration',{
        beforeEach(){
            this.data={
                partner:{
                    fields:{
                        display_name:{string:"Displayedname",type:"char",searchable:true},
                    },
                    records:[
                        {id:1,display_name:"LocomotiveBreath"},
                        {id:2,display_name:"HeyMacarena"},
                    ],
                },
            };
        },
    },function(){

        QUnit.module('GoogleDriveActionMenus');

        QUnit.test('renderingofthegoogledriveattachmentsinactionmenus',asyncfunction(assert){
            assert.expect(3);

            constform=awaittestUtils.createView({
                actionMenusRegistry:true,
                arch:
                    `<formstring="Partners">
                        <fieldname="display_name"/>
                    </form>`,
                data:this.data,
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/dataset/call_kw/google.drive.config/get_google_drive_config':
                            assert.deepEqual(args.args,['partner',1],
                                'Theroutetogetgoogledriveconfigshouldhavebeencalled');
                            return[{
                                id:27,
                                name:'CyberdyneSystems',
                            }];
                        case'/web/dataset/call_kw/google.drive.config/search_read':
                            return[{
                                google_drive_resource_id:"T1000",
                                google_drive_client_id:"cyberdyne.org",
                                id:1,
                            }];
                        case'/web/dataset/call_kw/google.drive.config/get_google_drive_url':
                            assert.deepEqual(args.args,[27,1,'T1000'],
                                'TheroutetogettheGoogleurlshouldhavebeencalled');
                            return;//donotreturnanythingoritwillopenanewtab.
                    }
                },
                model:'partner',
                res_id:1,
                View:FormView,
                viewOptions:{
                    hasActionMenus:true,
                },
            });
            awaitcpHelpers.toggleActionMenu(form);

            assert.containsOnce(form,'.oe_share_gdoc_item',
                "Thebuttontothegoogleactionshouldbepresent");

            awaitcpHelpers.toggleMenuItem(form,"CyberdyneSystems");

            form.destroy();
        });

        QUnit.test("nogoogledrivedata",asyncfunction(assert){
            assert.expect(1);

            constform=awaittestUtils.createView({
                actionMenusRegistry:true,
                arch:
                    `<formstring="Partners">
                        <fieldname="display_name"/>
                    </form>`,
                data:this.data,
                model:'partner',
                res_id:1,
                View:FormView,
                viewOptions:{
                    hasActionMenus:true,
                    ids:[1,2],
                    index:0,
                },
            });

            assert.containsNone(form,".o_cp_action_menus.o_embed_menu");

            form.destroy();
        });

        QUnit.test('clickonthegoogledriveattachmentsafterswitchingrecords',asyncfunction(assert){
            assert.expect(4);

            letcurrentRecordId=1;
            constform=awaittestUtils.createView({
                actionMenusRegistry:true,
                arch:
                    `<formstring="Partners">
                        <fieldname="display_name"/>
                    </form>`,
                data:this.data,
                asyncmockRPC(route,args){
                    switch(route){
                        case'/web/dataset/call_kw/google.drive.config/get_google_drive_config':
                            assert.deepEqual(args.args,['partner',currentRecordId],
                                'Theroutetogetgoogledriveconfigshouldhavebeencalled');
                            return[{
                                id:27,
                                name:'CyberdyneSystems',
                            }];
                        case'/web/dataset/call_kw/google.drive.config/search_read':
                            return[{
                                google_drive_resource_id:"T1000",
                                google_drive_client_id:"cyberdyne.org",
                                id:1,
                            }];
                        case'/web/dataset/call_kw/google.drive.config/get_google_drive_url':
                            assert.deepEqual(args.args,[27,currentRecordId,'T1000'],
                                'TheroutetogettheGoogleurlshouldhavebeencalled');
                            return;//donotreturnanythingoritwillopenanewtab.
                    }
                },
                model:'partner',
                res_id:1,
                View:FormView,
                viewOptions:{
                    hasActionMenus:true,
                    ids:[1,2],
                    index:0,
                },
            });

            awaitcpHelpers.toggleActionMenu(form);
            awaitcpHelpers.toggleMenuItem(form,"CyberdyneSystems");

            currentRecordId=2;
            awaitcpHelpers.pagerNext(form);

            awaitcpHelpers.toggleActionMenu(form);
            awaitcpHelpers.toggleMenuItem(form,"CyberdyneSystems");

            form.destroy();
        });
    });
});
