flectra.define("website.tour.unsplash_beacon",function(require){
"usestrict";

consttour=require("web_tour.tour");

tour.register("test_unsplash_beacon",{
    test:true,
    url:"/",
},[{
    content:"Verifywhetherbeaconwassent.",
    trigger:'img[data-beacon="sent"]',
    run:()=>{},//Thisisacheck.
}]);
});
