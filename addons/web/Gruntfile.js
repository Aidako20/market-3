module.exports=function(grunt){

    grunt.initConfig({
        jshint:{
            src:['static/src/**/*.js','static/tests/**/*.js'],
            options:{
                sub:true,//[]insteadof.
                evil:true,//eval
                laxbreak:true,//unsafelinebreaks
            },
        },
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');

    grunt.registerTask('test',[]);

    grunt.registerTask('default',['jshint']);

};