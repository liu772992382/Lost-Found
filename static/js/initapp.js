// Initialize your app
var myApp = new Framework7();

// Export selectors engine
var $$ = Framework7.$;

// Add view
var mainView = myApp.addView('.view-main', {
    // Because we use fixed-through navbar we can enable dynamic navbar
    dynamicNavbar: true
});

$$('#File').change(function() {
  a=$$(this).val().toLowerCase().split('.')
  if(a[a.length-1]=='png'||a[a.length-1]=='jpeg'||a[a.length-1]=='jpg'||a[a.length-1]=='bmp'){
  }
  else{
    this.outerHTML += '';
    this.value ="";
    myApp.alert('请上传正确的图片格式(*.jpg,*.png,*.jpeg,*.bmp)', "");
  }
});

$$(".publish-info").on('click', function() {
  myApp.addNotification({
        title: '温馨提示',
        message: '发布的启事需要经过管理员审核才能显示在首页'
    });
});

// 送网薪
$$(".send-money").click(function() {
  // 判断网薪是否小于100
  var money = $$(".send-money>div>div>i").text();
  if (parseInt(money) < 100) {
    myApp.alert("您的网薪不足100，请先赚足网薪再赠送吧~");
    $$(this).attr("href","#");
    return false;
  }
  // 判断是否通过校方认证

});

$$(".form-to-json").on('click', function() {
  var formData = myApp.formToJSON('#my-form');
  if (!formData.Content) {
    myApp.alert("写一点吧~", "");
    return false;
  }
  myApp.showPreloader();
  $$.ajax({
    type: "POST",
    url: "/found/feedback",
    data: formData,
    success: function(result) {
        myApp.hidePreloader();
        var result = JSON.parse(result);
        if (result.status == "success") {
          myApp.alert("感谢您的建议~", "");
          window.location.href = "/found/user";
        }
        else {
          myApp.alert("糟糕，出了点问题~", "");
          window.location.href = "/found/user";
        }
    },
    error: function(error) {
      myApp.hidePreloader();
      window.location.href = "/found/user";
    }
  });
});

$$('.ac-one').on('click', function() {
  var buttons1 = [
    {
        text: '分享至',
        label: true
    },
    {
      text: "<img src='/static/img/icon/yiban.png' class='icon-yiban' style='margin-right: -5px;' />&nbsp;&nbsp;易班",
      color: 'gray'
    },
    {
      text: "<img src='/static/img/icon/qq.jpg' class='icon-qq' />&nbsp;&nbsp;&nbsp;QQ",
      color: 'gray'
    },
    {
      text: "<img src='/static/img/icon/wechat.jpg' class='icon-wechat' />&nbsp;&nbsp;微信",
      color: 'gray'
    }
  ];
  var buttons2 = [
        {
            text: '取消',
            color: 'red'
        }
    ];
  var groups = [buttons1, buttons2];
  myApp.actions(groups);
});


$$(".get-money").on('click', function() {
  myApp.confirm("感谢您使用失物招领~", "确认领取", function() {
    myApp.alert("领取成功~");
  })
});

$$(".send-money").on('click', function() {
    //发送ajax请求
    myApp.showPreloader();
    $$.ajax({
      type: "GET",
      url: "/found/friend/me_list",
      success: function(result) {
          myApp.hidePreloader();
          var result = JSON.parse(result);
          if (result.status == "success") {
            var friend_list = result.info.list;
            for (x in friend_list) {
              $$(".yiban-friend-list").append(
                "<div class='list-group'><ul><li>" +
                      '<label class="item-content label-radio"><input type="radio" name="my-radio" value="' +
                      friend_list[x].yb_userid + '" checked="checked" />' +
                        '<div class="item-media">'+
                          '<img src="'+ friend_list[x].yb_userhead +'" class="search-user-img" /></div>'+
                        '<div class="item-inner"><div class="item-title">' +
                        friend_list[x].yb_username + '</div></div></label></li></ul></div>'
              )
            }
          }
          else {
            myApp.alert("糟糕，出了点问题~", "");
            window.location.href = "/found/user";
          }
      },
      error: function(error) {
        myApp.hidePreloader();
        window.location.href = "/found/user";
      }
    });
});

// $$(".form-to-json").on('click', function() {
//   var formData = myApp.formToJSON('#my-form');
//   // 验证易班id
//   var myreg = /^\d{7}$/;
//   if (!myreg.test(formData.yb_userid)) {
//     myApp.alert("请输入正确的易班id", "");
//     return false;
//   }
//   // 验证网薪
//   var number = parseInt(formData.award);
//   if (number < 100 || number % 100 != 0) {
//     myApp.alert("请输入正确的网薪数量", "");
//     return false;
//   }
//   // 发送ajax请求
//   myApp.showPreloader();
//   $$.ajax({
//     type: "GET",
//     url: "/found/school/award_wx",
//     data: formData,
//     success: function(result) {
//         myApp.hidePreloader();
//         var result = JSON.parse(result);
//         if (result.status == "success") {
//           myApp.alert("赠送成功， TA会感谢您的， 嘿嘿~", "");
//           window.location.href = "/found/user";
//         }
//         else {
//           myApp.alert("糟糕，出了点问题~", "");
//           window.location.href = "/found/user";
//         }
//     },
//     error: function(error) {
//       myApp.hidePreloader();
//       window.location.href = "/found/user";
//     }
//   });
// });
