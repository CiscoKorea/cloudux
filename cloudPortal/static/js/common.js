;(function(){
$.fn.customRadioCheck = function() {

  return this.each(function() {

    var $this = $(this);
    var $span = $('<span/>');

    $span.addClass('custom-'+ ($this.is(':checkbox') ? 'check' : 'radio'));
    $this.is(':checked') && $span.addClass('checked'); // init
    $span.insertAfter($this);

    $this.parent('label').addClass('custom-label')
      .attr('onclick', ''); // Fix clicking label in iOS
    // hide by shifting left
    $this.css({ position: 'absolute', left: '-9999px' });

    // Events
    $this.on({
      change: function() {
        if ($this.is(':radio')) {
          $this.parent().siblings('label')
            .find('.custom-radio').removeClass('checked');
        }
        $span.toggleClass('checked', $this.is(':checked'));
      },
      focus: function() { $span.addClass('focus'); },
      blur: function() { $span.removeClass('focus'); }
    });
  });
};
}());

function wrapWindowByMask(){
	var maskHeight = $(window).height();  
	
	$(".wrap").append("<div class=\"mask\"></div>");
	$('.mask').css({'height':maskHeight});  
	$('.mask').fadeTo("",0.3);    
	$(window).resize(function() {
		var maskHeight = $(window).height();  
		$('.mask').css({'height':maskHeight});  
	});

}


// 레이어팝업 열기
function layer_popup(area){
	var win_wd = $(window).width();
	var win_height = $(window).height();
	var wd = $(area).width();
	var wh = $(area).height();
	$(area).css({"left":(win_wd - wd)/2,"top":(win_height - wh)/2,"z-index":10000}).addClass("on");

	$(window).resize(function() {
		var win_wd = $(window).width();
		var win_height = $(window).height();
		var wd = $(area).width();
		var wh = $(area).height();
		$(area).css({"left":(win_wd - wd)/2,"top":(win_height - wh)/2,"z-index":10000});
	});
	wrapWindowByMask();
}

// 레이어팝업 닫기
function layer_close(btn){
	$(document).on('click',btn,function(){
		$(this).parents(".lay_pop").removeClass("on");
		$('.mask').remove();
		return false;
	});
}

//테이블 tbl-list 접근성 반영
function tbl_list(){
	var v_tbl = $(".inner").find("table");
	var v_summary = v_tbl.attr("summary");
	var v_caption = v_tbl.find("caption");
	var v_hth = v_tbl.find("thead th");
	var v_bth = v_tbl.find("tbody th");        //summary체크
	if(v_summary != true){
		var title = [];
		v_tbl.each(function(index, domEle){
			
			console.log(this);
			if ($(this).children("thead").length){
				$(this).find("thead tr th").each(function(){
					title.push($(this).text());
				});
				title = title.join(",")
				if($(this).hasClass('entbl')){
					 $(this).attr("summary","A "+title+" consisting of a table"); //영문화면에는 테이블에 entbl 클래스를 추가해서 영문타이틀을 대체텍스트로 추가
				}else{
					if($(this).attr("summary") == undefined){
						$(this).attr("summary",title+" 로 구성된 표입니다.");	
						$("<caption>"+title+" 로 구성된 표입니다.</caption>").insertBefore($(this).find("thead"));  
					}
				};
				title = [];
			} else {
				$(this).find("th").each(function(){
					title.push($(this).text());
				});
				title = title.join(",")
				if($(this).hasClass('entbl')){
					 $(this).attr("summary","A "+title+" consisting of a table"); //영문화면에는 테이블에 entbl 클래스를 추가해서 영문타이틀을 대체텍스트로 추가
				}else{
					if($(this).attr("summary") == undefined){
						$(this).attr("summary",title+" 로 구성된 표입니다.");	
						$("<caption>"+title+" 로 구성된 표입니다.</caption>").insertBefore($(this).find("tbody"));  
					}
				};
				title = [];
			}
		});
	}
	//scope체크
	if($(v_hth).attr("scope") != true){
		$(v_hth).attr("scope","col");
	}
	if($(v_bth).attr("scope") != true){
		$(v_bth).attr("scope","row");
	}

}


$(document).ready(function() {	
	// 레이어팝업 닫기
	layer_close('.lay_pop .btn_close');
	layer_close('.lay_pop .btn_cancel');
	tbl_list();
	$("body").find("select").wrap("<span class='styled-select'></span>")


	var col_right = $(document).width() - 238;
	var Height = $(document).height();
	var Height_doc = $(document).height();  
	$('.col_left').css({'height':Height_doc});  
	$('.col_right').css({'min-height':Height}).css({'width':col_right});  
	$(window).resize(function() {
		var col_right = $(document).width() - 238;
		var Height = $(document).height();
		var Height_doc = $(document).height();  
		$('.col_left').css({'height':Height_doc});  
		$('.col_right').css({'min-height':Height}).css({'width':col_right});  
	});
	
	
    $(".sub").hide();
    $(".create_list > h3 > a").click(function(){
        $(".sub:visible").slideUp("middle");
        $(".create_list > h3 > a").removeClass("on");
        $(this).addClass("on");
		$(this).parent().next('.sub:hidden').slideDown("middle");
        return false;
    })	

    $(".create_list .sub .box > .main_group > p > a").click(function(){
        $(this).find("span").toggleClass("on").parent().parent().parent().next('.sub_group').toggle();
        return false;
    })	

    $(".tree ul li a").click(function(){
        $(this).next('ul').toggle();
        $(this).parent().toggleClass("on");
        return false;
    })	

    $("#per1").click(function(){
        $(".lay_pop .lay_content table .none_tr").hide();
        return false;
    })	

    $("#per2").click(function(){
        $(".lay_pop .lay_content table .none_tr").show();
        return false;
    })	

});
