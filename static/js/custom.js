// 封装弹窗layer组件等
var common_ops = {
  alert:function( msg ,cb ){
      layer.alert( msg,{
          yes:function( index ){
              if( typeof cb == "function" ){
                  cb();
              }
              layer.close( index );
          }
      });
  },
  confirm:function( msg,callback ){
      callback = ( callback != undefined )?callback: { 'ok':null, 'cancel':null };
      layer.confirm( msg , {
          btn: ['确定','取消'] //按钮
      }, function( index ){
          //确定事件
          if( typeof callback.ok == "function" ){
              callback.ok();
          }
          layer.close( index );
      }, function( index ){
          //取消事件
          if( typeof callback.cancel == "function" ){
              callback.cancel();
          }
          layer.close( index );
      });
  },
  tip:function( msg,target ){
      layer.tips( msg, target, {
          //tips: [ 3, '#e5004f']
          tips: [ 3, '#00e5ca']
      });
      $('html, body').animate({
          scrollTop: target.offset().top - 10
      }, 100);
  }
};

// 功能
$(document).ready(function() {
  var chatBtn = $('#chatBtn');
  var chatInput = $('#chatInput');
  var chatWindow = $('#chatWindow');

  // 转义html代码，防止在浏览器渲染
  function escapeHtml(html) {
    var text = document.createTextNode(html);
    var div = document.createElement('div');
    div.appendChild(text);
    return div.innerHTML;
  }
  
  // 添加请求消息到窗口
  function addRequestMessage(message) {
    $(".answer .tips").css({"display":"none"});    // 打赏卡隐藏
    chatInput.val('');
    let escapedMessage = escapeHtml(message);// 对请求message进行转义，防止输入的是html而被浏览器渲染
    let requestMessageElement = $('<div class="row message-bubble"><img class="chat-icon" src="./static/images/用户.png"><div class="message-text resquest">' +  escapedMessage + '</div></div>');
    chatWindow.append(requestMessageElement);
    let responseMessageElement = $('<div class="row message-bubble"><img class="chat-icon" src="./static/images/机器人.png"><div class="message-text response"><div class="loading"><img src="./static/images/l.gif"></div></div></div>');
    chatWindow.append(responseMessageElement);
    chatWindow.animate({ scrollTop: chatWindow.prop('scrollHeight') }, 500);
  }
  // 添加响应消息到窗口
  function addResponseMessage(message) {
    let lastResponseElement = $(".message-bubble .response").last();
    lastResponseElement.empty();
    let escapedMessage = marked(message)  // 响应消息markdown实时转换为html
    lastResponseElement.append(escapedMessage);
    chatWindow.animate({ scrollTop: chatWindow.prop('scrollHeight') }, 500);
  }

  // 添加失败信息到窗口
  function addFailMessage(message) {
    let lastResponseElement = $(".message-bubble .response").last();
    lastResponseElement.empty();
    lastResponseElement.append(message);
    chatWindow.animate({ scrollTop: chatWindow.prop('scrollHeight') }, 500);

  }
  // 处理用户输入
  chatBtn.click(function() {
    // 解绑键盘事件
    chatInput.off("keydown",handleEnter);
    
    // ajax上传数据
    let data = {}
    let message = chatInput.val();
    if (message.length == 0){
      common_ops.alert("请输入内容！",function(){
        chatInput.val('');
        // 重新绑定键盘事件
        chatInput.on("keydown",handleEnter);
      })
      return
    }
    if(message ==="结束") {

        window.location.href = "/chat";
        return
    }
    addRequestMessage(message);
    // 收到回复前让按钮不可点击
    chatBtn.attr('disabled',true)
    data["prompt"] = JSON.stringify(message)
    // 发送信息到后台
    $.ajax({
      url: '/chat1',
      method: 'POST',
      data: data,
      xhrFields: {
        prevResponseLength : 0,
        onprogress: function(e) {
          var res = e.target.responseText;
          addResponseMessage(res);
        }
      },
      success:function(res){
        // 收到回复，让按钮可点击
        chatBtn.attr('disabled',false)
        // 重新绑定键盘事件
        chatInput.on("keydown",handleEnter);
        // 将最终回复添加到数组
      },
      error: function(jqXHR, textStatus, errorThrown) {
        addFailMessage('<p class="error">' + '出错啦！请稍后再试!' + '</p>');
        chatBtn.attr('disabled',false)
        chatInput.on("keydown",handleEnter);
      }
    });
  });
  // Enter键盘事件
  function handleEnter(e){
    if (e.keyCode==13){
      chatBtn.click();
      e.preventDefault();  //避免回车换行
    }
  }
  // 绑定Enter键盘事件
  chatInput.on("keydown",handleEnter);
});