flectra.define('web.test_utils_graph',function(){
"usestrict";

/**
 *GraphTestUtils
 *
 *Thismoduledefinesvariousutilityfunctionstohelptestgraphviews.
 *
 *Notethatallmethodsdefinedinthismoduleareexportedinthemain
 *testUtilsfile.
 */


/**
 *Reloadsagraphview.
 *
 *@param{GraphController}graph
 *@param{[Object]}paramsgiventothecontrollerreloadmethod
 */
functionreload(graph,params){
    returngraph.reload(params);
}

return{
    reload:reload,
};

});
