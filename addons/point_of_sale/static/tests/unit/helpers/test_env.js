flectra.define('point_of_sale.test_env',asyncfunction(require){
    'usestrict';

    /**
     *ManycomponentsinPoSaredependentonthePosModelinstance(pos).
     *Therefore,forunitteststhatrequireposintheComponents'env,we
     *preparedhereatestenvmaker(makePosTestEnv)basedon
     *makeTestEnvironmentofweb.
     */

    constmakeTestEnvironment=require('web.test_env');
    constenv=require('web.env');
    constmodels=require('point_of_sale.models');
    constRegistries=require('point_of_sale.Registries');

    Registries.Component.add(owl.misc.Portal);

    awaitenv.session.is_bound;
    constpos=newmodels.PosModel({
        rpc:env.services.rpc,
        session:env.session,
        do_action:async()=>{},
        setLoadingMessage:()=>{},
        setLoadingProgress:()=>{},
        showLoadingSkip:()=>{},
    });
    awaitpos.ready;

    /**
     *@param{Object}envdefaultenv
     *@param{Function}providedRPCmockrpc
     *@param{Function}providedDoActionmockdo_action
     */
    functionmakePosTestEnv(env={},providedRPC=null,providedDoAction=null){
        env=Object.assign(env,{pos});
        letposEnv=makeTestEnvironment(env,providedRPC);
        //ReplacerpcinthePosModelinstanceafterloading
        //datafromtheserversothateverysucceedingrpccalls
        //madebyposaremockedbytheprovidedRPC.
        pos.rpc=posEnv.rpc;
        pos.do_action=providedDoAction;
        returnposEnv;
    }

    returnmakePosTestEnv;
});
