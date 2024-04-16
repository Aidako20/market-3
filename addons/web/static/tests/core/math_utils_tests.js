flectra.define('web.math_utils_tests',function(require){
"usestrict";

varmathUtils=require('web.mathUtils');
varcartesian=mathUtils.cartesian;

QUnit.module('mathUtils',function(){

    QUnit.module('cartesian');


    QUnit.test('cartesianproductofzeroarrays',function(assert){
        assert.expect(1);
        assert.deepEqual(cartesian(),[undefined],
            "theunitoftheproductisasingleton");
    });

    QUnit.test('cartesianproductofasinglearray',function(assert){
        assert.expect(5);
        assert.deepEqual(cartesian([]),[]);
        assert.deepEqual(cartesian([1]),[1],
            "wedon'twantunecessarybrackets");
        assert.deepEqual(cartesian([1,2]),[1,2]);
        assert.deepEqual(cartesian([[1,2]]),[[1,2]],
            "theinternalstructureofelementsshouldbepreserved");
        assert.deepEqual(cartesian([[1,2],[3,[2]]]),[[1,2],[3,[2]]],
            "theinternalstructureofelementsshouldbepreserved");
    });

    QUnit.test('cartesianproductoftwoarrays',function(assert){
        assert.expect(5);
        assert.deepEqual(cartesian([],[]),[]);
        assert.deepEqual(cartesian([1],[]),[]);
        assert.deepEqual(cartesian([1],[2]),[[1,2]]);
        assert.deepEqual(cartesian([1,2],[3]),[[1,3],[2,3]]);
        assert.deepEqual(cartesian([[1],4],[2,[3]]),[[[1],2],[[1],[3]],[4,2],[4,[3]]],
            "theinternalstructureofelementsshouldbepreserved");
    });

    QUnit.test('cartesianproductofthreearrays',function(assert){
        assert.expect(4);
        assert.deepEqual(cartesian([],[],[]),[]);
        assert.deepEqual(cartesian([1],[],[2,5]),[]);
        assert.deepEqual(cartesian([1],[2],[3]),[[1,2,3]],
            "weshouldhavenounecessarybrackets,wewantelementstobe'triples'");
        assert.deepEqual(cartesian([[1],2],[3],[4]),[[[1],3,4],[2,3,4]],
            "theinternalstructureofelementsshouldbepreserved");
    });

    QUnit.test('cartesianproductoffourarrays',function(assert){
        assert.expect(1);
        assert.deepEqual(cartesian([1],[2],[3],[4]),[[1,2,3,4]]);
    });

});
});
