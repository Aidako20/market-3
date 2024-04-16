flectra.define('web.py_utils_tests',function(require){
"usestrict";

varContext=require('web.Context');
varpyUtils=require('web.py_utils');
vartime=require('web.time');
vartestUtils=require('web.test_utils');

constr=String.raw;

QUnit.assert.checkAST=function(expr,message){
    varast=pyUtils._getPyJSAST(expr);
    varformattedAST=pyUtils._formatAST(ast);
    this.pushResult({
        result:expr===formattedAST,
        actual:formattedAST,
        expected:expr,
        message:message
    });
};

QUnit.module('core',function(){

    QUnit.module('py_utils');

    QUnit.test('simplepythonexpression',function(assert){
        assert.expect(2);

        varresult=pyUtils.py_eval("TrueandFalse");
        assert.strictEqual(result,false,"shouldproperlyevaluatebasicexpression");
        result=pyUtils.py_eval("a+b",{a:1,b:41});
        assert.strictEqual(result,42,"shouldproperlyevaluatebasicsum");
    });

    QUnit.test('simplearithmetic',function(assert){
        assert.expect(3);

        varresult=pyUtils.py_eval("1+2");
        assert.strictEqual(result,3,"shouldproperlyevaluatesum");
        result=pyUtils.py_eval("42%5");
        assert.strictEqual(result,2,"shouldproperlyevaluatemodulooperator");
        result=pyUtils.py_eval("2**3");
        assert.strictEqual(result,8,"shouldproperlyevaluatepoweroperator");
    });


    QUnit.test('notprefix',function(assert){
        assert.expect(3);

        assert.ok(py.eval('notFalse'));
        assert.ok(py.eval('notfoo',{foo:false}));
        assert.ok(py.eval('notainb',{a:3,b:[1,2,4,8]}));
    });


    functionmakeTimeCheck(assert){
        varcontext=pyUtils.context();
        returnfunction(expr,func,message){
            //evaluateexprbetweentwocallstonewDate(),andcheckthat
            //theresultisbetweenthetransformeddates
            vard0=newDate();
            varresult=py.eval(expr,context);
            vard1=newDate();
            assert.ok(func(d0)<=result&&result<=func(d1),message);
        };
    }

    //Portfrompypy/lib_pypy/test_datetime.py
    functionmakeEq(assert,c2){
        varctx=pyUtils.context();
        varc=_.extend({td:ctx.datetime.timedelta},c2||{});
        returnfunction(a,b,message){
            assert.ok(py.eval(a+'=='+b,c),message);
        };
    }

    QUnit.test('strftime',function(assert){
        assert.expect(3);

        varcheck=makeTimeCheck(assert);

        check("time.strftime('%Y')",function(d){
            returnString(d.getFullYear());
        });

        check("time.strftime('%Y')+'-01-30'",function(d){
            returnString(d.getFullYear())+'-01-30';
        });

        check("time.strftime('%Y-%m-%d%H:%M:%S')",function(d){
            return_.str.sprintf('%04d-%02d-%02d%02d:%02d:%02d',
                d.getUTCFullYear(),d.getUTCMonth()+1,d.getUTCDate(),
                d.getUTCHours(),d.getUTCMinutes(),d.getUTCSeconds());
        });
    });

    QUnit.test('context_today',function(assert){
        assert.expect(1);

        varcheck=makeTimeCheck(assert,pyUtils);

        check("context_today().strftime('%Y-%m-%d')",function(d){
            returnString(_.str.sprintf('%04d-%02d-%02d',
                d.getFullYear(),d.getMonth()+1,d.getDate()));
        });
    });

    QUnit.test('timedelta.test_constructor',function(assert){
        assert.expect(16);

        vareq=makeEq(assert);

        //keywordargstoconstructor
        eq('td()','td(weeks=0,days=0,hours=0,minutes=0,seconds=0,'+
                        'milliseconds=0,microseconds=0)');
        eq('td(1)','td(days=1)');
        eq('td(0,1)','td(seconds=1)');
        eq('td(0,0,1)','td(microseconds=1)');
        eq('td(weeks=1)','td(days=7)');
        eq('td(days=1)','td(hours=24)');
        eq('td(hours=1)','td(minutes=60)');
        eq('td(minutes=1)','td(seconds=60)');
        eq('td(seconds=1)','td(milliseconds=1000)');
        eq('td(milliseconds=1)','td(microseconds=1000)');

        //Checkfloatargstoconstructor
        eq('td(weeks=1.0/7)','td(days=1)');
        eq('td(days=1.0/24)','td(hours=1)');
        eq('td(hours=1.0/60)','td(minutes=1)');
        eq('td(minutes=1.0/60)','td(seconds=1)');
        eq('td(seconds=0.001)','td(milliseconds=1)');
        eq('td(milliseconds=0.001)','td(microseconds=1)');
    });

    QUnit.test('timedelta.test_computations',function(assert){
        assert.expect(28);

        varc=pyUtils.context();
        varzero=py.float.fromJSON(0);
        vareq=makeEq(assert,{
            //oneweek
            a:py.PY_call(c.datetime.timedelta,[
                py.float.fromJSON(7)]),
            //oneminute
            b:py.PY_call(c.datetime.timedelta,[
                zero,py.float.fromJSON(60)]),
            //onemillisecond
            c:py.PY_call(c.datetime.timedelta,[
                zero,zero,py.float.fromJSON(1000)]),
        });

        eq('a+b+c','td(7,60,1000)');
        eq('a-b','td(6,24*3600-60)');
        eq('-a','td(-7)');
        eq('+a','td(7)');
        eq('-b','td(-1,24*3600-60)');
        eq('-c','td(-1,24*3600-1,999000)');
        //eq('abs(a)','a');
        //eq('abs(-a)','a');
        eq('td(6,24*3600)','a');
        eq('td(0,0,60*1000000)','b');
        eq('a*10','td(70)');
        eq('a*10','10*a');
        //eq('a*10L','10*a');
        eq('b*10','td(0,600)');
        eq('10*b','td(0,600)');
        //eq('b*10L','td(0,600)');
        eq('c*10','td(0,0,10000)');
        eq('10*c','td(0,0,10000)');
        //eq('c*10L','td(0,0,10000)');
        eq('a*-1','-a');
        eq('b*-2','-b-b');
        eq('c*-2','-c+-c');
        eq('b*(60*24)','(b*60)*24');
        eq('b*(60*24)','(60*b)*24');
        eq('c*1000','td(0,1)');
        eq('1000*c','td(0,1)');
        eq('a//7','td(1)');
        eq('b//10','td(0,6)');
        eq('c//1000','td(0,0,1)');
        eq('a//10','td(0,7*24*360)');
        eq('a//3600000','td(0,0,7*24*1000)');

        //Issue#11576
        eq('td(999999999,86399,999999)-td(999999999,86399,999998)','td(0,0,1)');
        eq('td(999999999,1,1)-td(999999999,1,0)',
            'td(0,0,1)');
    });

    QUnit.test('timedelta.test_basic_attributes',function(assert){
        assert.expect(3);

        varctx=pyUtils.context();
        assert.strictEqual(py.eval('datetime.timedelta(1,7,31).days',ctx),1);
        assert.strictEqual(py.eval('datetime.timedelta(1,7,31).seconds',ctx),7);
        assert.strictEqual(py.eval('datetime.timedelta(1,7,31).microseconds',ctx),31);
    });

    QUnit.test('timedelta.test_total_seconds',function(assert){
        assert.expect(6);

        varc={timedelta:pyUtils.context().datetime.timedelta};
        assert.strictEqual(py.eval('timedelta(365).total_seconds()',c),31536000);
        assert.strictEqual(
            py.eval('timedelta(seconds=123456.789012).total_seconds()',c),
            123456.789012);
        assert.strictEqual(
            py.eval('timedelta(seconds=-123456.789012).total_seconds()',c),
            -123456.789012);
        assert.strictEqual(
            py.eval('timedelta(seconds=0.123456).total_seconds()',c),0.123456);
        assert.strictEqual(py.eval('timedelta().total_seconds()',c),0);
        assert.strictEqual(
            py.eval('timedelta(seconds=1000000).total_seconds()',c),1e6);
    });

    QUnit.test('timedelta.test_str',function(assert){
        assert.expect(10);

        varc={td:pyUtils.context().datetime.timedelta};

        assert.strictEqual(py.eval('str(td(1))',c),"1day,0:00:00");
        assert.strictEqual(py.eval('str(td(-1))',c),"-1day,0:00:00");
        assert.strictEqual(py.eval('str(td(2))',c),"2days,0:00:00");
        assert.strictEqual(py.eval('str(td(-2))',c),"-2days,0:00:00");

        assert.strictEqual(py.eval('str(td(hours=12,minutes=58,seconds=59))',c),
                    "12:58:59");
        assert.strictEqual(py.eval('str(td(hours=2,minutes=3,seconds=4))',c),
                        "2:03:04");
        assert.strictEqual(
            py.eval('str(td(weeks=-30,hours=23,minutes=12,seconds=34))',c),
            "-210days,23:12:34");

        assert.strictEqual(py.eval('str(td(milliseconds=1))',c),"0:00:00.001000");
        assert.strictEqual(py.eval('str(td(microseconds=3))',c),"0:00:00.000003");

        assert.strictEqual(
            py.eval('str(td(days=999999999,hours=23,minutes=59,seconds=59,microseconds=999999))',c),
            "999999999days,23:59:59.999999");
    });

    QUnit.test('timedelta.test_massive_normalization',function(assert){
        assert.expect(3);

        vartd=py.PY_call(
            pyUtils.context().datetime.timedelta,
            {microseconds:py.float.fromJSON(-1)});
        assert.strictEqual(td.days,-1);
        assert.strictEqual(td.seconds,24*3600-1);
        assert.strictEqual(td.microseconds,999999);
    });

    QUnit.test('timedelta.test_bool',function(assert){
        assert.expect(5);

        varc={td:pyUtils.context().datetime.timedelta};
        assert.ok(py.eval('bool(td(1))',c));
        assert.ok(py.eval('bool(td(0,1))',c));
        assert.ok(py.eval('bool(td(0,0,1))',c));
        assert.ok(py.eval('bool(td(microseconds=1))',c));
        assert.ok(py.eval('bool(nottd(0))',c));
    });

    QUnit.test('date.test_computations',function(assert){
        assert.expect(31);

        vard=pyUtils.context().datetime;

        vara=d.date.fromJSON(2002,1,31);
        varb=d.date.fromJSON(1956,1,31);
        assert.strictEqual(
            py.eval('(a-b).days',{a:a,b:b}),
            46*365+12);
        assert.strictEqual(py.eval('(a-b).seconds',{a:a,b:b}),0);
        assert.strictEqual(py.eval('(a-b).microseconds',{a:a,b:b}),0);

        varday=py.PY_call(d.timedelta,[py.float.fromJSON(1)]);
        varweek=py.PY_call(d.timedelta,[py.float.fromJSON(7)]);
        a=d.date.fromJSON(2002,3,2);
        varctx={
            a:a,
            day:day,
            week:week,
            date:d.date
        };
        assert.ok(py.eval('a+day==date(2002,3,3)',ctx));
        assert.ok(py.eval('day+a==date(2002,3,3)',ctx));//5
        assert.ok(py.eval('a-day==date(2002,3,1)',ctx));
        assert.ok(py.eval('-day+a==date(2002,3,1)',ctx));
        assert.ok(py.eval('a+week==date(2002,3,9)',ctx));
        assert.ok(py.eval('a-week==date(2002,2,23)',ctx));
        assert.ok(py.eval('a+52*week==date(2003,3,1)',ctx));//10
        assert.ok(py.eval('a-52*week==date(2001,3,3)',ctx));
        assert.ok(py.eval('(a+week)-a==week',ctx));
        assert.ok(py.eval('(a+day)-a==day',ctx));
        assert.ok(py.eval('(a-week)-a==-week',ctx));
        assert.ok(py.eval('(a-day)-a==-day',ctx));//15
        assert.ok(py.eval('a-(a+week)==-week',ctx));
        assert.ok(py.eval('a-(a+day)==-day',ctx));
        assert.ok(py.eval('a-(a-week)==week',ctx));
        assert.ok(py.eval('a-(a-day)==day',ctx));

        assert.throws(function(){
            py.eval('a+1',ctx);
        },/^Error:TypeError:/);//20
        assert.throws(function(){
            py.eval('a-1',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('1+a',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('1-a',ctx);
        },/^Error:TypeError:/);

        //delta-dateissenseless.
        assert.throws(function(){
            py.eval('day-a',ctx);
        },/^Error:TypeError:/);
        //mixingdateand(deltaordate)via*or//issenseless
        assert.throws(function(){
            py.eval('day*a',ctx);
        },/^Error:TypeError:/);//25
        assert.throws(function(){
            py.eval('a*day',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('day//a',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('a//day',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('a*a',ctx);
        },/^Error:TypeError:/);
        assert.throws(function(){
            py.eval('a//a',ctx);
        },/^Error:TypeError:/);//30
        //date+dateissenseless
        assert.throws(function(){
            py.eval('a+a',ctx);
        },/^Error:TypeError:/);

    });

    QUnit.test('add',function(assert){
        assert.expect(2);
        assert.strictEqual(
            py.eval("(datetime.datetime(2017,4,18,9,32,15).add(hours=2,minutes=30,"+
                "seconds=10)).strftime('%Y-%m-%d%H:%M:%S')",pyUtils.context()),
            '2017-04-1812:02:25'
        );
        assert.strictEqual(
            py.eval("(datetime.date(2017,4,18).add(months=1,years=3,days=5))"+
                ".strftime('%Y-%m-%d')",pyUtils.context()),
            '2020-05-23'
        );
    });

    QUnit.test('subtract',function(assert){
        assert.expect(2);
        assert.strictEqual(
            py.eval("(datetime.datetime(2017,4,18,9,32,15).subtract(hours=1,minutes=5,"+
                "seconds=33)).strftime('%Y-%m-%d%H:%M:%S')",pyUtils.context()),
            '2017-04-1808:26:42'
        );
        assert.strictEqual(
            py.eval("(datetime.date(2017,4,18).subtract(years=5,months=1,days=1))"+
                ".strftime('%Y-%m-%d')",pyUtils.context()),
            '2012-03-17'
        );
    })

    QUnit.test('start_of/end_of',function(assert){
        assert.expect(26);

        vardatetime=pyUtils.context().datetime;
        //Ain'tthatakickinthehead?
        var_date=datetime.date.fromJSON(2281,10,11);
        var_datetime=datetime.datetime.fromJSON(2281,10,11,22,33,44);
        varctx={
            _date:_date,
            _datetime:_datetime,
            date:datetime.date,
            datetime:datetime.datetime
        };

        //Startofperiod
        //Datesfirst
        assert.ok(py.eval('_date.start_of("year")==date(2281,1,1)',ctx));
        assert.ok(py.eval('_date.start_of("quarter")==date(2281,10,1)',ctx));
        assert.ok(py.eval('_date.start_of("month")==date(2281,10,1)',ctx));
        assert.ok(py.eval('_date.start_of("week")==date(2281,10,10)',ctx));
        assert.ok(py.eval('_date.start_of("day")==date(2281,10,11)',ctx));
        assert.throws(function(){
            py.eval('_date.start_of("hour")',ctx);
        },/^Error:ValueError:/);

        //Datetimes
        assert.ok(py.eval('_datetime.start_of("year")==datetime(2281,1,1)',ctx));
        assert.ok(py.eval('_datetime.start_of("quarter")==datetime(2281,10,1)',ctx));
        assert.ok(py.eval('_datetime.start_of("month")==datetime(2281,10,1)',ctx));
        assert.ok(py.eval('_datetime.start_of("week")==datetime(2281,10,10)',ctx));
        assert.ok(py.eval('_datetime.start_of("day")==datetime(2281,10,11)',ctx));
        assert.ok(py.eval('_datetime.start_of("hour")==datetime(2281,10,11,22,0,0)',ctx));
        assert.throws(function(){
            py.eval('_datetime.start_of("cheese")',ctx);
        },/^Error:ValueError:/);

        //Endofperiod
        //Dates
        assert.ok(py.eval('_date.end_of("year")==date(2281,12,31)',ctx));
        assert.ok(py.eval('_date.end_of("quarter")==date(2281,12,31)',ctx));
        assert.ok(py.eval('_date.end_of("month")==date(2281,10,31)',ctx));
        assert.ok(py.eval('_date.end_of("week")==date(2281,10,16)',ctx));
        assert.ok(py.eval('_date.end_of("day")==date(2281,10,11)',ctx));
        assert.throws(function(){
            py.eval('_date.start_of("hour")',ctx);
        },/^Error:ValueError:/);

        //Datetimes
        assert.ok(py.eval('_datetime.end_of("year")==datetime(2281,12,31,23,59,59)',ctx));
        assert.ok(py.eval('_datetime.end_of("quarter")==datetime(2281,12,31,23,59,59)',ctx));
        assert.ok(py.eval('_datetime.end_of("month")==datetime(2281,10,31,23,59,59)',ctx));
        assert.ok(py.eval('_datetime.end_of("week")==datetime(2281,10,16,23,59,59)',ctx));
        assert.ok(py.eval('_datetime.end_of("day")==datetime(2281,10,11,23,59,59)',ctx));
        assert.ok(py.eval('_datetime.end_of("hour")==datetime(2281,10,11,22,59,59)',ctx));
        assert.throws(function(){
            py.eval('_datetime.end_of("cheese")',ctx);
        },/^Error:ValueError:/);
    });

    QUnit.test('relativedelta',function(assert){
        assert.expect(7);

        assert.strictEqual(
            py.eval("(datetime.date(2012,2,15)+relativedelta(days=-1)).strftime('%Y-%m-%d23:59:59')",
                    pyUtils.context()),
            "2012-02-1423:59:59");
        assert.strictEqual(
            py.eval("(datetime.date(2012,2,15)+relativedelta(days=1)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            "2012-02-16");
        assert.strictEqual(
            py.eval("(datetime.date(2012,2,15)+relativedelta(days=-1)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            "2012-02-14");
        assert.strictEqual(
            py.eval("(datetime.date(2012,2,1)+relativedelta(days=-1)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            '2012-01-31');
        assert.strictEqual(
            py.eval("(datetime.date(2015,2,5)+relativedelta(days=-6,weekday=0)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            '2015-02-02');
        assert.strictEqual(
            py.eval("(datetime.date(2018,2,1)+relativedelta(years=7,months=42,days=42)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            '2028-09-12');
        assert.strictEqual(
            py.eval("(datetime.date(2018,2,1)+relativedelta(years=-7,months=-42,days=-42)).strftime('%Y-%m-%d')",
                    pyUtils.context()),
            '2007-06-20');
    });


    QUnit.test('timedelta',function(assert){
        assert.expect(4);
        assert.strictEqual(
            py.eval("(datetime.datetime(2017,2,15,1,7,31)+datetime.timedelta(days=1)).strftime('%Y-%m-%d%H:%M:%S')",
                    pyUtils.context()),
            "2017-02-1601:07:31");
        assert.strictEqual(
            py.eval("(datetime.datetime(2012,2,15,1,7,31)-datetime.timedelta(hours=1)).strftime('%Y-%m-%d%H:%M:%S')",
                    pyUtils.context()),
            "2012-02-1500:07:31");
        assert.strictEqual(
            py.eval("(datetime.datetime(2012,2,15,1,7,31)+datetime.timedelta(hours=-1)).strftime('%Y-%m-%d%H:%M:%S')",
                    pyUtils.context()),
            "2012-02-1500:07:31");
        assert.strictEqual(
            py.eval("(datetime.datetime(2012,2,15,1,7,31)+datetime.timedelta(minutes=100)).strftime('%Y-%m-%d%H:%M:%S')",
                    pyUtils.context()),
            "2012-02-1502:47:31");
    });

    QUnit.test('datetime.tojson',function(assert){
        assert.expect(7);

        varresult=py.eval(
            'datetime.datetime(2012,2,15,1,7,31)',
            pyUtils.context());

        assert.ok(resultinstanceofDate);
        assert.strictEqual(result.getFullYear(),2012);
        assert.strictEqual(result.getMonth(),1);
        assert.strictEqual(result.getDate(),15);
        assert.strictEqual(result.getHours(),1);
        assert.strictEqual(result.getMinutes(),7);
        assert.strictEqual(result.getSeconds(),31);
    });


    QUnit.test('to_utcinoctoberwithwinter/summerchange',function(assert){
        assert.expect(7);

        constoriginalGetTimezoneOffset=Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset=function(){
            constmonth=this.getMonth()//startsat0;
            if(10<=month||month<=2){
                //roughapproximation
                return-60;
            }else{
                return-120;
            }
        }

        varresult=py.eval(
            "datetime.datetime(2022,10,17).to_utc()",
            pyUtils.context());

        assert.ok(resultinstanceofDate);
        assert.strictEqual(result.getFullYear(),2022);
        assert.strictEqual(result.getMonth(),9);
        assert.strictEqual(result.getDate(),16);
        assert.strictEqual(result.getHours(),22);
        assert.strictEqual(result.getMinutes(),0);
        assert.strictEqual(result.getSeconds(),0);

        Date.prototype.getTimezoneOffset=originalGetTimezoneOffset;
    });

    QUnit.test('datetime.combine',function(assert){
        assert.expect(2);

        varresult=py.eval(
            'datetime.datetime.combine(datetime.date(2012,2,15),'+
            '                         datetime.time(1,7,13))'+
            '  .strftime("%Y-%m-%d%H:%M:%S")',
            pyUtils.context());
        assert.strictEqual(result,"2012-02-1501:07:13");

        result=py.eval(
            'datetime.datetime.combine(datetime.date(2012,2,15),'+
            '                         datetime.time())'+
            '  .strftime("%Y-%m-%d%H:%M:%S")',
            pyUtils.context());
        assert.strictEqual(result,'2012-02-1500:00:00');
    });

    QUnit.test('datetime.replace',function(assert){
        assert.expect(1);

        varresult=py.eval(
            'datetime.datetime(2012,2,15,1,7,13)'+
            '  .replace(hour=0,minute=0,second=0)'+
            '  .strftime("%Y-%m-%d%H:%M:%S")',
            pyUtils.context());
        assert.strictEqual(result,"2012-02-1500:00:00");
    });

    QUnit.test('conditionalexpressions',function(assert){
        assert.expect(2);
        assert.strictEqual(
            py.eval('1ifaelse2',{a:true}),
            1
        );
        assert.strictEqual(
            py.eval('1ifaelse2',{a:false}),
            2
        );
    });

    QUnit.module('py_utils(evaldomaincontexts)',{
        beforeEach:function(){
            this.user_context={
                uid:1,
                lang:'en_US',
                tz:false,
            };
        },
    });


    QUnit.test('empty,basic',function(assert){
        assert.expect(3);

        varresult=pyUtils.eval_domains_and_contexts({
            contexts:[this.user_context],
            domains:[],
        });

        //defaultvaluesfornewdb
        assert.deepEqual(result.context,{
            lang:'en_US',
            tz:false,
            uid:1
        });
        assert.deepEqual(result.domain,[]);
        assert.deepEqual(result.group_by,[]);
    });


    QUnit.test('context_merge_00',function(assert){
        assert.expect(1);

        varctx=[
            {
                "__contexts":[
                    {"lang":"en_US","tz":false,"uid":1},
                    {
                        "active_id":8,
                        "active_ids":[8],
                        "active_model":"sale.order",
                        "bin_raw":true,
                        "default_composition_mode":"comment",
                        "default_model":"sale.order",
                        "default_res_id":8,
                        "default_template_id":18,
                        "default_use_template":true,
                        "edi_web_url_view":"faaaake",
                        "lang":"en_US",
                        "mark_so_as_sent":null,
                        "show_address":null,
                        "tz":false,
                        "uid":null
                    },
                    {}
                ],
                "__eval_context":null,
                "__ref":"compound_context"
            },
            {"active_id":9,"active_ids":[9],"active_model":"mail.compose.message"}
        ];
        varresult=pyUtils.eval_domains_and_contexts({
            contexts:ctx,
            domins:[],
        });

        assert.deepEqual(result.context,{
            active_id:9,
            active_ids:[9],
            active_model:'mail.compose.message',
            bin_raw:true,
            default_composition_mode:'comment',
            default_model:'sale.order',
            default_res_id:8,
            default_template_id:18,
            default_use_template:true,
            edi_web_url_view:"faaaake",
            lang:'en_US',
            mark_so_as_sent:null,
            show_address:null,
            tz:false,
            uid:null
        });

    });

    QUnit.test('context_merge_01',function(assert){
        assert.expect(1);

        varctx=[{
            "__contexts":[
                {
                    "lang":"en_US",
                    "tz":false,
                    "uid":1
                },
                {
                    "default_attachment_ids":[],
                    "default_body":"",
                    "default_model":"res.users",
                    "default_parent_id":false,
                    "default_res_id":1
                },
                {}
            ],
            "__eval_context":null,
            "__ref":"compound_context"
        }];
        varresult=pyUtils.eval_domains_and_contexts({
            contexts:ctx,
            domains:[],
        });

        assert.deepEqual(result.context,{
            "default_attachment_ids":[],
            "default_body":"",
            "default_model":"res.users",
            "default_parent_id":false,
            "default_res_id":1,
            "lang":"en_US",
            "tz":false,
            "uid":1
        });
    });

    QUnit.test('domainwithtime',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval_domains_and_contexts({
            domains:[
                [['type','=','contract']],
                ["|",["state","in",["open","draft"]],[["type","=","contract"],["state","=","pending"]]],
                "['|','&',('date','!=',False),('date','<=',time.strftime('%Y-%m-%d')),('is_overdue_quantity','=',True)]",
                [['user_id','=',1]]
            ],
            contexts:[],
        });

        vard=newDate();
        vartoday=_.str.sprintf("%04d-%02d-%02d",
                d.getUTCFullYear(),d.getUTCMonth()+1,d.getUTCDate());
        assert.deepEqual(result.domain,[
            ["type","=","contract"],
            "|",["state","in",["open","draft"]],
                 [["type","=","contract"],
                  ["state","=","pending"]],
            "|",
                "&",["date","!=",false],
                        ["date","<=",today],
                ["is_overdue_quantity","=",true],
            ["user_id","=",1]
        ]);
    });

    QUnit.test('conditionalcontext',function(assert){
        assert.expect(2);

        vard={
            __ref:'domain',
            __debug:"[('company_id','=',context.get('company_id',False))]"
        };

        varresult1=pyUtils.eval_domains_and_contexts({
            domains:[d],
            contexts:[],
        });
        assert.deepEqual(result1.domain,[['company_id','=',false]]);

        varresult2=pyUtils.eval_domains_and_contexts({
            domains:[d],
            contexts:[],
            eval_context:{company_id:42},
        });
        assert.deepEqual(result2.domain,[['company_id','=',42]]);
    });

    QUnit.test('substitutionincontext',function(assert){
        assert.expect(1);

        //setup(session);
        varc="{'default_opportunity_id':active_id,'default_duration':1.0,'lng':lang}";
        varcc=newContext(c);
        cc.set_eval_context({active_id:42});
        varresult=pyUtils.eval_domains_and_contexts({
            domains:[],contexts:[this.user_context,cc]
        });

        assert.deepEqual(result.context,{
            lang:"en_US",
            tz:false,
            uid:1,
            default_opportunity_id:42,
            default_duration:1.0,
            lng:"en_US"
        });
    });

    QUnit.test('date',function(assert){
        assert.expect(1);

        vard="[('state','!=','cancel'),('opening_date','>',context_today().strftime('%Y-%m-%d'))]";
        varresult=pyUtils.eval_domains_and_contexts({
            domains:[d],
            contexts:[],
        });

        vardate=newDate();
        vartoday=_.str.sprintf("%04d-%02d-%02d",
            date.getFullYear(),date.getMonth()+1,date.getDate());
        assert.deepEqual(result.domain,[
            ['state','!=','cancel'],
            ['opening_date','>',today]
        ]);
    });

    QUnit.test('delta',function(assert){
        assert.expect(1);

        vard="[('type','=','in'),('day','<=',time.strftime('%Y-%m-%d')),('day','>',(context_today()-datetime.timedelta(days=15)).strftime('%Y-%m-%d'))]";
        varresult=pyUtils.eval_domains_and_contexts({
            domains:[d],
            contexts:[],
        });
        vardate=newDate();
        vartoday=_.str.sprintf("%04d-%02d-%02d",
            date.getFullYear(),date.getMonth()+1,date.getDate());
        date.setDate(date.getDate()-15);
        varago_15_d=_.str.sprintf("%04d-%02d-%02d",
            date.getFullYear(),date.getMonth()+1,date.getDate());
        assert.deepEqual(result.domain,[
            ['type','=','in'],
            ['day','<=',today],
            ['day','>',ago_15_d]
        ]);
    });

    QUnit.test('horrorfromthedeep',function(assert){
        assert.expect(1);

        varcs=[
            {"__ref":"compound_context",
                "__contexts":[
                    {"__ref":"context","__debug":"{'k':'foo,'+str(context.get('test_key',False))}"},
                    {"__ref":"compound_context",
                        "__contexts":[
                            {"lang":"en_US","tz":false,"uid":1},
                            {"lang":"en_US","tz":false,"uid":1,
                                "active_model":"sale.order","default_type":"out",
                                "show_address":1,"contact_display":"partner_address",
                                "active_ids":[9],"active_id":9},
                            {}
                        ],"__eval_context":null},
                    {"active_id":8,"active_ids":[8],
                        "active_model":"stock.picking.out"},
                    {"__ref":"context","__debug":"{'default_ref':'stock.picking.out,'+str(context.get('active_id',False))}","__id":"54d6ad1d6c45"}
                ],"__eval_context":null}
        ];
        varresult=pyUtils.eval_domains_and_contexts({
            domains:[],
            contexts:cs,
        });

        assert.deepEqual(result.context,{
            k:'foo,False',
            lang:'en_US',
            tz:false,
            uid:1,
            active_model:'stock.picking.out',
            active_id:8,
            active_ids:[8],
            default_type:'out',
            show_address:1,
            contact_display:'partner_address',
            default_ref:'stock.picking.out,8'
        });
    });

    QUnit.module('py_utils(contexts)');

    QUnit.test('context_recursive',function(assert){
        assert.expect(3);

        varcontext_to_eval=[{
            __ref:'context',
            __debug:'{"foo":context.get("bar","qux")}'
        }];
        assert.deepEqual(
            pyUtils.eval('contexts',context_to_eval,{bar:"ok"}),
            {foo:'ok'});
        assert.deepEqual(
            pyUtils.eval('contexts',context_to_eval,{bar:false}),
            {foo:false});
        assert.deepEqual(
            pyUtils.eval('contexts',context_to_eval),
            {foo:'qux'});
    });

    QUnit.test('context_sequences',function(assert){
        assert.expect(1);

        //Contextnshouldhavebaseevaluationcontext+allofcontexts
        //0..n-1initsownevaluationcontext
        varactive_id=4;
        varresult=pyUtils.eval('contexts',[
            {
                "__contexts":[
                    {
                        "department_id":false,
                        "lang":"en_US",
                        "project_id":false,
                        "section_id":false,
                        "tz":false,
                        "uid":1
                    },
                    {"search_default_create_uid":1},
                    {}
                ],
                "__eval_context":null,
                "__ref":"compound_context"
            },
            {
                "active_id":active_id,
                "active_ids":[active_id],
                "active_model":"purchase.requisition"
            },
            {
                "__debug":"{'record_id':active_id}",
                "__id":"63e8e9bff8a6",
                "__ref":"context"
            }
        ]);

        assert.deepEqual(result,{
            department_id:false,
            lang:'en_US',
            project_id:false,
            section_id:false,
            tz:false,
            uid:1,
            search_default_create_uid:1,
            active_id:active_id,
            active_ids:[active_id],
            active_model:'purchase.requisition',
            record_id:active_id
        });
    });

    QUnit.test('non-literal_eval_contexts',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('contexts',[{
            "__ref":"compound_context",
            "__contexts":[
                {"__ref":"context","__debug":"{'move_type':parent.move_type}",
                    "__id":"462b9dbed42f"}
            ],
            "__eval_context":{
                "__ref":"compound_context",
                "__contexts":[{
                        "__ref":"compound_context",
                        "__contexts":[
                            {"__ref":"context","__debug":"{'move_type':move_type}",
                                "__id":"16a04ed5a194"}
                        ],
                        "__eval_context":{
                            "__ref":"compound_context",
                            "__contexts":[
                                {"lang":"en_US","tz":false,"uid":1,
                                    "journal_type":"sale","section_id":false,
                                    "default_move_type":"out_invoice",
                                    "move_type":"out_invoice","department_id":false},
                                {"id":false,"journal_id":10,
                                    "number":false,"move_type":"out_invoice",
                                    "currency_id":1,"partner_id":4,
                                    "fiscal_position_id":false,
                                    "invoice_date":false,"date":false,
                                    "payment_term_id":false,
                                    "reference":false,"account_id":440,
                                    "name":false,"invoice_line_ids":[],
                                    "tax_line_ids":[],"amount_untaxed":0,
                                    "amount_tax":0,"reconciled":false,
                                    "amount_total":0,"state":"draft",
                                    "amount_residual":0,"company_id":1,
                                    "date_due":false,"user_id":1,
                                    "partner_bank_id":false,"origin":false,
                                    "move_id":false,"comment":false,
                                    "payment_ids":[[6,false,[]]],
                                    "active_id":false,"active_ids":[],
                                    "active_model":"account.move",
                                    "parent":{}}
                    ],"__eval_context":null}
                },{
                    "id":false,
                    "product_id":4,
                    "name":"[PC1]BasicPC",
                    "quantity":1,
                    "uom_id":1,
                    "price_unit":100,
                    "account_id":853,
                    "discount":0,
                    "account_analytic_id":false,
                    "company_id":false,
                    "note":false,
                    "invoice_line_tax_ids":[[6,false,[1]]],
                    "active_id":false,
                    "active_ids":[],
                    "active_model":"account.move.line",
                    "parent":{
                        "id":false,"journal_id":10,"number":false,
                        "move_type":"out_invoice","currency_id":1,
                        "partner_id":4,"fiscal_position_id":false,
                        "invoice_date":false,"date":false,
                        "payment_term_id":false,
                        "reference":false,"account_id":440,"name":false,
                        "tax_line_ids":[],"amount_untaxed":0,"amount_tax":0,
                        "reconciled":false,"amount_total":0,
                        "state":"draft","amount_residual":0,"company_id":1,
                        "date_due":false,"user_id":1,
                        "partner_bank_id":false,"origin":false,
                        "move_id":false,"comment":false,
                        "payment_ids":[[6,false,[]]]}
                }],
                "__eval_context":null
            }
        }]);

        assert.deepEqual(result,{move_type:'out_invoice'});
    });

    QUnit.test('return-input-value',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('contexts',[{
            __ref:'compound_context',
            __contexts:["{'line_id':line_id,'journal_id':journal_id}"],
            __eval_context:{
                __ref:'compound_context',
                __contexts:[{
                    __ref:'compound_context',
                    __contexts:[
                        {lang:'en_US',tz:'Europe/Paris',uid:1},
                        {lang:'en_US',tz:'Europe/Paris',uid:1},
                        {}
                    ],
                    __eval_context:null,
                },{
                    active_id:false,
                    active_ids:[],
                    active_model:'account.move',
                    amount:0,
                    company_id:1,
                    id:false,
                    journal_id:14,
                    line_id:[
                        [0,false,{
                            account_id:55,
                            amount_currency:0,
                            analytic_account_id:false,
                            credit:0,
                            currency_id:false,
                            date_maturity:false,
                            debit:0,
                            name:"dscsd",
                            partner_id:false,
                            tax_line_id:false,
                        }]
                    ],
                    name:'/',
                    narration:false,
                    parent:{},
                    partner_id:false,
                    date:'2011-01-1',
                    ref:false,
                    state:'draft',
                    to_check:false,
                }],
                __eval_context:null,
            },
        }]);
        assert.deepEqual(result,{
            journal_id:14,
            line_id:[[0,false,{
                account_id:55,
                amount_currency:0,
                analytic_account_id:false,
                credit:0,
                currency_id:false,
                date_maturity:false,
                debit:0,
                name:"dscsd",
                partner_id:false,
                tax_line_id:false,
            }]],
        });
    });

    QUnit.module('py_utils(domains)');

    QUnit.test('current_date',function(assert){
        assert.expect(1);

        varcurrent_date=time.date_to_str(newDate());
        varresult=pyUtils.eval('domains',
            [[],{"__ref":"domain","__debug":"[('name','>=',current_date),('name','<=',current_date)]","__id":"5dedcfc96648"}],
            pyUtils.context());
        assert.deepEqual(result,[
            ['name','>=',current_date],
            ['name','<=',current_date]
        ]);
    });

    QUnit.test('context_freevar',function(assert){
        assert.expect(3);

        vardomains_to_eval=[{
            __ref:'domain',
            __debug:'[("foo","=",context.get("bar","qux"))]'
        },[['bar','>=',42]]];
        assert.deepEqual(
            pyUtils.eval('domains',domains_to_eval,{bar:"ok"}),
            [['foo','=','ok'],['bar','>=',42]]);
        assert.deepEqual(
            pyUtils.eval('domains',domains_to_eval,{bar:false}),
            [['foo','=',false],['bar','>=',42]]);
        assert.deepEqual(
            pyUtils.eval('domains',domains_to_eval),
            [['foo','=','qux'],['bar','>=',42]]);
    });

    QUnit.module('py_utils(groupbys)');

    QUnit.test('groupbys_00',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {group_by:['bar','qux']},
            {group_by:null},
            {group_by:'grault'}
        ]);
        assert.deepEqual(result,['foo','bar','qux','grault']);
    });

    QUnit.test('groupbys_01',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {__ref:'context',__debug:'{"group_by":"bar"}'},
            {group_by:'grault'}
        ]);
        assert.deepEqual(result,['foo','bar','grault']);
    });

    QUnit.test('groupbys_02',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {
                __ref:'compound_context',
                __contexts:[{group_by:'bar'}],
                __eval_context:null
            },
            {group_by:'grault'}
        ]);
        assert.deepEqual(result,['foo','bar','grault']);
    });

    QUnit.test('groupbys_03',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {
                __ref:'compound_context',
                __contexts:[
                    {__ref:'context',__debug:'{"group_by":value}'}
                ],
                __eval_context:{value:'bar'}
            },
            {group_by:'grault'}
        ]);
        assert.deepEqual(result,['foo','bar','grault']);
    });

    QUnit.test('groupbys_04',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {
                __ref:'compound_context',
                __contexts:[
                    {__ref:'context',__debug:'{"group_by":value}'}
                ],
                __eval_context:{value:'bar'}
            },
            {group_by:'grault'}
        ],{value:'bar'});
        assert.deepEqual(result,['foo','bar','grault']);
    });

    QUnit.test('groupbys_05',function(assert){
        assert.expect(1);

        varresult=pyUtils.eval('groupbys',[
            {group_by:'foo'},
            {__ref:'context',__debug:'{"group_by":value}'},
            {group_by:'grault'}
        ],{value:'bar'});
        assert.deepEqual(result,['foo','bar','grault']);
    });

    QUnit.module('pyutils(_formatAST)');

    QUnit.test("basicvalues",function(assert){
        assert.expect(6);

        assert.checkAST("1","integervalue");
        assert.checkAST("1.4","floatvalue");
        assert.checkAST("-12","negativeintegervalue");
        assert.checkAST("True","boolean");
        assert.checkAST(`"somestring"`,"astring");
        assert.checkAST("None","None");
    });

    QUnit.test("dictionary",function(assert){
        assert.expect(3);

        assert.checkAST("{}","emptydictionary");
        assert.checkAST(`{"a":1}`,"dictionarywithasinglekey");
        assert.checkAST(`d["a"]`,"getavalueinadictionary");
    });

    QUnit.test("list",function(assert){
        assert.expect(2);

        assert.checkAST("[]","emptylist");
        assert.checkAST("[1]","listwithonevalue");
    });

    QUnit.test("tuple",function(assert){
        assert.expect(2);

        assert.checkAST("()","emptytuple");
        assert.checkAST("(1,2)","basictuple");
    });

    QUnit.test("simplearithmetic",function(assert){
        assert.expect(15);

        assert.checkAST("1+2","addition");
        assert.checkAST("+(1+2)","otheraddition,prefix");
        assert.checkAST("1-2","substraction");
        assert.checkAST("-1-2","othersubstraction");
        assert.checkAST("-(1+2)","othersubstraction");
        assert.checkAST("1+2+3","additionof3integers");
        assert.checkAST("a+b","additionoftwovariables");
        assert.checkAST("42%5","modulooperator");
        assert.checkAST("a*10","multiplication");
        assert.checkAST("a**10","**");
        assert.checkAST("~10","bitwisenot");
        assert.checkAST("~(10+3)","bitwisenot");
        assert.checkAST("a*(1+2)","multiplicationandaddition");
        assert.checkAST("(a+b)*43","additionandmultiplication");
        assert.checkAST("a//10","integerdivision");
    });

    QUnit.test("booleanoperators",function(assert){
        assert.expect(6);

        assert.checkAST("TrueandFalse","booleanoperator");
        assert.checkAST("TrueorFalse","booleanoperatoror");
        assert.checkAST("(TrueorFalse)andFalse","booleanoperatorsandandor");
        assert.checkAST("notFalse","notprefix");
        assert.checkAST("notfoo","notprefixwithvariable");
        assert.checkAST("notainb","notprefixwithexpression");
    });

    QUnit.test("conditionalexpression",function(assert){
        assert.expect(2);

        assert.checkAST("1ifaelse2");
        assert.checkAST("[]ifaelse2");
    });

    QUnit.test("otheroperators",function(assert){
        assert.expect(7);

        assert.checkAST("x==y","==operator");
        assert.checkAST("x!=y","!=operator");
        assert.checkAST("x<y","<operator");
        assert.checkAST("xisy","isoperator");
        assert.checkAST("xisnoty","isandnotoperator");
        assert.checkAST("xiny","inoperator");
        assert.checkAST("xnotiny","notinoperator");
    });

    QUnit.test("equality",function(assert){
        assert.expect(1);
        assert.checkAST("a==b","simpleequality");
    });

    QUnit.test("strftime",function(assert){
        assert.expect(3);
        assert.checkAST(`time.strftime("%Y")`,"strftimewithyear");
        assert.checkAST(`time.strftime("%Y")+"-01-30"`,"strftimewithyear");
        assert.checkAST(`time.strftime("%Y-%m-%d%H:%M:%S")`,"strftimewithyear");
    });

    QUnit.test("context_today",function(assert){
        assert.expect(1);
        assert.checkAST(`context_today().strftime("%Y-%m-%d")`,"contexttodaycall");
    });


    QUnit.test("functioncall",function(assert){
        assert.expect(5);
        assert.checkAST("td()","simplecall");
        assert.checkAST("td(a,b,c)","simplecallwithargs");
        assert.checkAST('td(days=1)',"simplecallwithkwargs");
        assert.checkAST('f(1,2,days=1)',"mixingargsandkwargs");
        assert.checkAST('str(td(2))',"functioncallinfunctioncall");
    });

    QUnit.test("variousexpressions",function(assert){
        assert.expect(3);
        assert.checkAST('(a-b).days',"substractionand.days");
        assert.checkAST('a+day==date(2002,3,3)');

        varexpr=`[("type","=","in"),("day","<=",time.strftime("%Y-%m-%d")),("day",">",(context_today()-datetime.timedelta(days=15)).strftime("%Y-%m-%d"))]`;
        assert.checkAST(expr);
    });

    QUnit.test('escapingsupport',function(assert){
        assert.expect(4);
        assert.strictEqual(py.eval(r`"\x61"`),"a","hexescapes");
        assert.strictEqual(py.eval(r`"\\abc"`),r`\abc`,"escapedbackslash");
        assert.checkAST(r`"\\abc"`,"escapedbackslashASTcheck");

        const{_getPyJSAST,_formatAST}=pyUtils;
        consta=r`'foo\\abc"\''`;
        constb=_formatAST(_getPyJSAST(_formatAST(_getPyJSAST(a))));
        //OurreprusesJSON.stringifywhichalwaysusesdoublequotes,
        //whereasPython'sreprissingle-quote-biased:stringsarerepr'd
        //usingsinglequotedelimiters*unless*theycontainsinglequotesand
        //nodoublequotes,thenthey'redelimitedwithdoublequotes.
        assert.strictEqual(b,r`"foo\\abc\"'"`);
    });

    QUnit.module('pyutils(_normalizeDomain)');

    QUnit.assert.checkNormalization=function(domain,normalizedDomain){
        normalizedDomain=normalizedDomain||domain;
        varresult=pyUtils.normalizeDomain(domain);
        this.pushResult({
            result:result===normalizedDomain,
            actual:result,
            expected:normalizedDomain
        });
    };


    QUnit.test("returnsimple(normalized)domains",function(assert){
        assert.expect(3);

        assert.checkNormalization("[]");
        assert.checkNormalization(`[("a","=",1)]`);
        assert.checkNormalization(`["!",("a","=",1)]`);
    });

    QUnit.test("properlyaddthe&inanonnormalizeddomain",function(assert){
        assert.expect(1);
        assert.checkNormalization(
            `[("a","=",1),("b","=",2)]`,
            `["&",("a","=",1),("b","=",2)]`
        );
    });

    QUnit.test("normalizedomainwith!operator",function(assert){
        assert.expect(1);
        assert.checkNormalization(
            `["!",("a","=",1),("b","=",2)]`,
            `["&","!",("a","=",1),("b","=",2)]`
        );
    });

    QUnit.module('pyutils(assembleDomains)');

    QUnit.assert.checkAssemble=function(domains,operator,domain){
        domain=pyUtils.normalizeDomain(domain);
        varresult=pyUtils.assembleDomains(domains,operator);
        this.pushResult({
            result:result===domain,
            actual:result,
            expected:domain
        });
    };

    QUnit.test("assembledomains",function(assert){
        assert.expect(7);

        assert.checkAssemble([],'&',"[]");
        assert.checkAssemble(["[('a','=',1)]"],null,"[('a','=',1)]");
        assert.checkAssemble(
            ["[('a','=','1'),('b','!=',2)]"],
            'AND',
            "['&',('a','=','1'),('b','!=',2)]"
        );
        assert.checkAssemble(
            ["[('a','=','1')]","[]"],
            'AND',
            "[('a','=','1')]"
        );
        assert.checkAssemble(
            ["[('a','=','1')]","[('b','<=',3)]"],
            'AND',
            "['&',('a','=','1'),('b','<=',3)]"
        );
        assert.checkAssemble(
            ["[('a','=','1'),('c','in',[4,5])]","[('b','<=',3)]"],
            'OR',
            "['|','&',('a','=','1'),('c','in',[4,5]),('b','<=',3)]"
        );
        assert.checkAssemble(
            ["[('user_id','=',uid)]"],
            null,
            "[('user_id','=',uid)]"
        );
    });
});
});
