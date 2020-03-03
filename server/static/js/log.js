function scrollToBottom(){
    var scrollHeight = $('#log-input').prop('scrollHeight');
    $('#log-input').scrollTop(scrollHeight, 500);
}


$(function() {
    scrollToBottom();
    $('.REFRESH').on('click',(e)=>{
        e.preventDefault();
        $('#log-input').text('');
        $.ajax({
            url: '/getlog',
            type: 'GET',
            success: function(res) {
                var data = JSON.parse(res);
                if(data.code == 0) {
                    console.log('日志获取成功');
                    let log = data.log;
                    $('#log-input').text(log);
                    scrollToBottom();
                }else{
                    console.error('日志获取失败');
                }
            },
            error:function() {
                console.error('服务器异常','日志获取失败');
            }
        })
    });

});
