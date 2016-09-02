$(document).ready(function() {

  //处理公告鼠标事件
  $(".notice").hover(function() {
    $(this).css("width", "400px");
  }, function() {
    $(this).css("width", "24px");
  });

  //处理图片上方显示标题事件
  $(".gallery-item").hover(function() {
    $(".header-top").css("height", "40px");
  }, function() {
    $(".header-top").css("height", "0");
  });

  //加载更多
  $(".load").click(function() {
    for (var i=0; i<8; i++) {
      $(this).prev().append("<div class='gallery-item'>" +
          '<img src="test.jpg"  alt="远方 有一个地方 那里种有我们的梦想"/>' +
          '<div class="describe"> \
            <p>寻物</p> \
            <div class="gallery-desc"> \
              <p>丢失地点: 松园二栋楼下架空层</p> \
              <p>丢失时间: 2016年4月6日晚10点</p> \
              <p style="word-break: break-all;">相关描述: 一个黑色的swiss书包，里面有一个白色计算器，一些草稿纸，还有两只笔。</p> \
            </div> \
          </div>' + "</div>");
    }
  });
});
