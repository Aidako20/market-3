flectra.define('web.sample_server_tests',function(require){
    "usestrict";

    constSampleServer=require('web.SampleServer');
    constsession=require('web.session');
    const{mock}=require('web.test_utils');

    const{
        MAIN_RECORDSET_SIZE,SEARCH_READ_LIMIT,//Limits
        SAMPLE_COUNTRIES,SAMPLE_PEOPLE,SAMPLE_TEXTS,//Textvalues
        MAX_COLOR_INT,MAX_FLOAT,MAX_INTEGER,MAX_MONETARY,//Numbervalues
        SUB_RECORDSET_SIZE,//Recordssise
    }=SampleServer;

    /**
     *Transformsrandomresultsintodeterministicones.
     */
    classDeterministicSampleServerextendsSampleServer{
        constructor(){
            super(...arguments);
            this.arrayElCpt=0;
            this.boolCpt=0;
            this.subRecordIdCpt=0;
        }
        _getRandomArrayEl(array){
            returnarray[this.arrayElCpt++%array.length];
        }
        _getRandomBool(){
            returnBoolean(this.boolCpt++%2);
        }
        _getRandomSubRecordId(){
            return(this.subRecordIdCpt++%SUB_RECORDSET_SIZE)+1;
        }
    }

    QUnit.module("SampleServer",{
        beforeEach(){
            this.fields={
                'res.users':{
                    display_name:{string:"Name",type:'char'},
                    name:{string:"Reference",type:'char'},
                    email:{string:"Email",type:'char'},
                    phone_number:{string:"Phonenumber",type:'char'},
                    brol_machin_url_truc:{string:"URL",type:'char'},
                    urlemailphone:{string:"Whatever",type:'char'},
                    active:{string:"Active",type:'boolean'},
                    is_alive:{string:"Isalive",type:'boolean'},
                    description:{string:"Description",type:'text'},
                    birthday:{string:"Birthday",type:'date'},
                    arrival_date:{string:"Dateofarrival",type:'datetime'},
                    height:{string:"Height",type:'float'},
                    color:{string:"Color",type:'integer'},
                    age:{string:"Age",type:'integer'},
                    salary:{string:"Salary",type:'monetary'},
                    currency:{string:"Currency",type:'many2one',relation:'res.currency'},
                    manager_id:{string:"Manager",type:'many2one',relation:'res.users'},
                    cover_image_id:{string:"CoverImage",type:'many2one',relation:'ir.attachment'},
                    managed_ids:{string:"Managing",type:'one2many',relation:'res.users'},
                    tag_ids:{string:"Tags",type:'many2many',relation:'tag'},
                    type:{string:"Type",type:'selection',selection:[
                        ['client',"Client"],['partner',"Partner"],['employee',"Employee"]
                    ]},
                },
                'res.country':{
                    display_name:{string:"Name",type:'char'},
                },
                'hobbit':{
                    display_name:{string:"Name",type:'char'},
                    profession:{string:"Profession",type:'selection',selection:[
                        ['gardener',"Gardener"],['brewer',"Brewer"],['adventurer',"Adventurer"]
                    ]},
                    age:{string:"Age",type:'integer'},
                },
                'ir.attachment':{
                    display_name:{string:"Name",type:'char'},
                }
            };
        },
    },function(){

        QUnit.module("Basicbehaviour");

        QUnit.test("Sampledata:peopletype+allfieldnames",asyncfunction(assert){
            assert.expect(26);

            mock.patch(session,{
                company_currency_id:4,
            });

            constallFieldNames=Object.keys(this.fields['res.users']);
            constserver=newDeterministicSampleServer('res.users',this.fields['res.users']);
            const{records}=awaitserver.mockRpc({
                method:'/web/dataset/search_read',
                model:'res.users',
                fields:allFieldNames,
            });
            constrec=records[0];

            functionassertFormat(fieldName,regex){
                if(regexinstanceofRegExp){
                    assert.ok(
                        regex.test(rec[fieldName].toString()),
                        `Field"${fieldName}"hasthecorrectformat`
                    );
                }else{
                    assert.strictEqual(
                        typeofrec[fieldName],regex,
                        `Field"${fieldName}"isoftype${regex}`
                    );
                }
            }
            functionassertBetween(fieldName,min,max,isFloat=false){
                constval=rec[fieldName];
                assert.ok(
                    min<=val&&val<max&&(isFloat||parseInt(val,10)===val),
                    `Field"${fieldName}"isbetween${min}and${max}${!isFloat?'andisaninteger':''}:${val}`
                );
            }

            //Basicfields
            assert.ok(SAMPLE_PEOPLE.includes(rec.display_name));
            assert.ok(SAMPLE_PEOPLE.includes(rec.name));
            assert.strictEqual(rec.email,
                `${rec.display_name.replace(//,".").toLowerCase()}@sample.demo`
            );
            assertFormat('phone_number',/\+1555754000\d/);
            assertFormat('brol_machin_url_truc',/http:\/\/sample\d\.com/);
            assert.strictEqual(rec.urlemailphone,false);
            assert.strictEqual(rec.active,true);
            assertFormat('is_alive','boolean');
            assert.ok(SAMPLE_TEXTS.includes(rec.description));
            assertFormat('birthday',/\d{4}-\d{2}-\d{2}/);
            assertFormat('arrival_date',/\d{4}-\d{2}-\d{2}\d{2}:\d{2}:\d{2}/);
            assertBetween('height',0,MAX_FLOAT,true);
            assertBetween('color',0,MAX_COLOR_INT);
            assertBetween('age',0,MAX_INTEGER);
            assertBetween('salary',0,MAX_MONETARY);

            //checkfloatfieldhave2decimalrounding
            assert.strictEqual(rec.height,parseFloat(parseFloat(rec.height).toFixed(2)));

            constselectionValues=this.fields['res.users'].type.selection.map(
                (sel)=>sel[0]
            );
            assert.ok(selectionValues.includes(rec.type));

            //Relationalfields
            assert.strictEqual(rec.currency[0],4);
            //Currentlyweexpectthecurrencynametobealatinstring,which
            //isnotimportant;inmostcaseweonlyneedtheID.Thefollowing
            //assertioncanberemovedifneeded.
            assert.ok(SAMPLE_TEXTS.includes(rec.currency[1]));

            assert.strictEqual(typeofrec.manager_id[0],'number');
            assert.ok(SAMPLE_PEOPLE.includes(rec.manager_id[1]));

            assert.strictEqual(rec.cover_image_id,false);

            assert.strictEqual(rec.managed_ids.length,2);
            assert.ok(rec.managed_ids.every(
                (id)=>typeofid==='number')
            );

            assert.strictEqual(rec.tag_ids.length,2);
            assert.ok(rec.tag_ids.every(
                (id)=>typeofid==='number')
            );

            mock.unpatch(session);
        });

        QUnit.test("Sampledata:countrytype",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('res.country',this.fields['res.country']);
            const{records}=awaitserver.mockRpc({
                method:'/web/dataset/search_read',
                model:'res.country',
                fields:['display_name'],
            });

            assert.ok(SAMPLE_COUNTRIES.includes(records[0].display_name));
        });

        QUnit.test("Sampledata:anytype",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            const{records}=awaitserver.mockRpc({
                method:'/web/dataset/search_read',
                model:'hobbit',
                fields:['display_name'],
            });

            assert.ok(SAMPLE_TEXTS.includes(records[0].display_name));
        });

        QUnit.module("RPCcalls");

        QUnit.test("Send'search_read'RPC:validfieldnames",asyncfunction(assert){
            assert.expect(3);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'/web/dataset/search_read',
                model:'hobbit',
                fields:['display_name'],
            });

            assert.deepEqual(
                Object.keys(result.records[0]),
                ['id','display_name']
            );
            assert.strictEqual(result.length,SEARCH_READ_LIMIT);
            assert.ok(/\w+/.test(result.records[0].display_name),
                "Displaynamehasbeenmocked"
            );
        });

        QUnit.test("Send'search_read'RPC:invalidfieldnames",asyncfunction(assert){
            assert.expect(3);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'/web/dataset/search_read',
                model:'hobbit',
                fields:['name'],
            });

            assert.deepEqual(
                Object.keys(result.records[0]),
                ['id','name']
            );
            assert.strictEqual(result.length,SEARCH_READ_LIMIT);
            assert.strictEqual(result.records[0].name,false,
                `Field"name"doesn'texist=>returnsfalse`
            );
        });

        QUnit.test("Send'web_read_group'RPC:nogroup",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);
            server.setExistingGroups([]);

            constresult=awaitserver.mockRpc({
                method:'web_read_group',
                model:'hobbit',
                groupBy:['profession'],
            });

            assert.deepEqual(result,{groups:[],length:0});
        });

        QUnit.test("Send'web_read_group'RPC:2groups",asyncfunction(assert){
            assert.expect(5);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);
            constexistingGroups=[
                {profession:'gardener',profession_count:0},
                {profession:'adventurer',profession_count:0},
            ];
            server.setExistingGroups(existingGroups);

            constresult=awaitserver.mockRpc({
                method:'web_read_group',
                model:'hobbit',
                groupBy:['profession'],
                fields:[],
            });

            assert.strictEqual(result.length,2);
            assert.strictEqual(result.groups.length,2);

            assert.deepEqual(
                result.groups.map((g)=>g.profession),
                ["gardener","adventurer"]
            );

            assert.strictEqual(
                result.groups.reduce((acc,g)=>acc+g.profession_count,0),
                MAIN_RECORDSET_SIZE
            );
            assert.ok(
                result.groups.every((g)=>g.profession_count===g.__data.length)
            );
        });

        QUnit.test("Send'web_read_group'RPC:allgroups",asyncfunction(assert){
            assert.expect(5);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);
            constexistingGroups=[
                {profession:'gardener',profession_count:0},
                {profession:'brewer',profession_count:0},
                {profession:'adventurer',profession_count:0},
            ];
            server.setExistingGroups(existingGroups);

            constresult=awaitserver.mockRpc({
                method:'web_read_group',
                model:'hobbit',
                groupBy:['profession'],
                fields:[],
            });

            assert.strictEqual(result.length,3);
            assert.strictEqual(result.groups.length,3);

            assert.deepEqual(
                result.groups.map((g)=>g.profession),
                ["gardener","brewer","adventurer"]
            );

            assert.strictEqual(
                result.groups.reduce((acc,g)=>acc+g.profession_count,0),
                MAIN_RECORDSET_SIZE
            );
            assert.ok(
                result.groups.every((g)=>g.profession_count===g.__data.length)
            );
        });

        QUnit.test("Send'read_group'RPC:nogroup",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read_group',
                model:'hobbit',
                fields:[],
                groupBy:[],
            });

            assert.deepEqual(result,[{
                __count:MAIN_RECORDSET_SIZE,
                __domain:[],
            }]);
        });

        QUnit.test("Send'read_group'RPC:groupBy",asyncfunction(assert){
            assert.expect(3);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read_group',
                model:'hobbit',
                fields:[],
                groupBy:['profession'],
            });

            assert.strictEqual(result.length,3);
            assert.deepEqual(
                result.map((g)=>g.profession),
                ["adventurer","brewer","gardener"]
            );
            assert.strictEqual(
                result.reduce((acc,g)=>acc+g.profession_count,0),
                MAIN_RECORDSET_SIZE,
            );
        });

        QUnit.test("Send'read_group'RPC:groupByandfield",asyncfunction(assert){
            assert.expect(4);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read_group',
                model:'hobbit',
                fields:['age'],
                groupBy:['profession'],
            });

            assert.strictEqual(result.length,3);
            assert.deepEqual(
                result.map((g)=>g.profession),
                ["adventurer","brewer","gardener"]
            );
            assert.strictEqual(
                result.reduce((acc,g)=>acc+g.profession_count,0),
                MAIN_RECORDSET_SIZE,
            );
            assert.strictEqual(
                result.reduce((acc,g)=>acc+g.age,0),
                server.data.hobbit.records.reduce((acc,g)=>acc+g.age,0)
            );
        });

        QUnit.test("Send'read_group'RPC:multiplegroupBysandlazy",asyncfunction(assert){
            assert.expect(2);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read_group',
                model:'hobbit',
                fields:[],
                groupBy:['profession','age'],
            });

            assert.ok('profession'inresult[0]);
            assert.notOk('age'inresult[0]);
        });

        QUnit.test("Send'read_group'RPC:multiplegroupBysandnotlazy",asyncfunction(assert){
            assert.expect(2);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read_group',
                model:'hobbit',
                fields:[],
                groupBy:['profession','age'],
                lazy:false,
            });

            assert.ok('profession'inresult[0]);
            assert.ok('age'inresult[0]);
        });

        QUnit.test("Send'read'RPC:noid",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read',
                model:'hobbit',
                args:[
                    [],['display_name']
                ],
            });

            assert.deepEqual(result,[]);
        });

        QUnit.test("Send'read'RPC:oneid",asyncfunction(assert){
            assert.expect(3);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constresult=awaitserver.mockRpc({
                method:'read',
                model:'hobbit',
                args:[
                    [1],['display_name']
                ],
            });

            assert.strictEqual(result.length,1);
            assert.ok(
                /\w+/.test(result[0].display_name),
                "Displaynamehasbeenmocked"
            );
            assert.strictEqual(result[0].id,1);
        });

        QUnit.test("Send'read'RPC:morethanallavailableids",asyncfunction(assert){
            assert.expect(1);

            constserver=newDeterministicSampleServer('hobbit',this.fields.hobbit);

            constamount=MAIN_RECORDSET_SIZE+3;
            constids=newArray(amount).fill().map((_,i)=>i+1);
            constresult=awaitserver.mockRpc({
                method:'read',
                model:'hobbit',
                args:[
                    ids,['display_name']
                ],
            });

            assert.strictEqual(result.length,MAIN_RECORDSET_SIZE);
        });

        //Tobeimplementedifneeded
        //QUnit.test("Send'read_progress_bar'RPC",asyncfunction(assert){...});
    });
});
