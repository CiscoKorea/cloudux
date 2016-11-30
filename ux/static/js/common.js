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
function layer_popup_close(area){
    $(area).removeClass("on");
    $('.mask').remove();
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
        $(this).parent().parent().children().children('ul').hide();
        $(this).next('ul').show();
        $(this).parent().parent().children().removeClass("on")
        $(this).parent().toggleClass("on");
        return false;
    })

	$(".tree.vswitch ul li a").click(function(){
        searchVswitch(this);
        return false;
    })

    $("#per1").click(function(){
        //$(".lay_pop .lay_content table .none_tr").hide();
        //return false;
    })	

    $("#per2").click(function(){
        //$(".lay_pop .lay_content table .none_tr").show();
        //return false;
    })	

});


function searchVswitch(me) {
	//console.log($(me).data("vswitchid"))
	if($(".tree.vswitch ul li.on").length > 0) {
		$("tr[class^='pgl']").hide()
		$(".tree.vswitch ul li.on").each(function (index, element) {
			var swid = $(element).data("vswitchid")
			$(".pgl" + swid).show()
		});
	} else {
		$("tr[class^='pgl']").show()
	}
}

////////// merge
function doColSpan(tid) {
    var colSpanCount = 1,
        tObj = document.getElementById(tid),
        i = tObj.rows.length,
        j,
        numCells,
        row,
        cell;
    while (i-- > 0) {
        row = tObj.rows[i];
        if (row) {
            j = 0;
            numCells = row.cells.length;
            while (j < numCells) {
                cell = row.cells[j];
                if (cell.innerHTML) {
                    if (colSpanCount > 1) {
                        colSpanCount--;
                        continue;
                    }
                    colSpanCount = getColSpanCount(tObj, i, j);
                    if (colSpanCount > 1) {
                        cell.colSpan = colSpanCount;
                    }
                }
            }
        }
    }
}
function getColSpanCount(tObj, i, j) {
    var colSpanCount = 1,
        nextX = parseInt(j, 10);
    while (isEqualToNextRightCell(tObj, i, j, ++nextX)) {
        colSpanCount++;
    }
    return colSpanCount;
}
function isEqualToNextRightCell(tObj, i, j, nextX){
    return tObj.rows[i].cells[nextX] &&
		tObj.rows[i].cells[j].innerHTML === tObj.rows[i].cells[nextX].innerHTML;
}
function doRowSpan(tid){
    var tObj=document.getElementById(tid);
    for(var i=0; i<tObj.rows.length; i++){
        if(tObj.rows[i]!=null){
            for(var j in tObj.rows[i].cells){
                if(tObj.rows[i].cells[j].innerHTML && j < 2){
                    rowSpanCount = getRowSpanCount(tObj, i, j);
                    if(rowSpanCount > 1){
                        tObj.rows[i].cells[j].rowSpan = rowSpanCount;
                    }
                }
            }
        }
    }
}
function getRowSpanCount(tObj, i, j){
    rowSpanCount = 1;
    nextY = parseInt(i);
    while(true){
        nextY++;
        if(isEqualToNextUnderCell(tObj, i, j, nextY)){
            rowSpanCount++;
            continue;
        }else{
            break;
        }
    }
    return rowSpanCount;
}
function isEqualToNextUnderCell(tObj, i, j, nextY){
    return tObj.rows[nextY] && tObj.rows[nextY].cells[j] && tObj.rows[i].cells[j].innerHTML == tObj.rows[nextY].cells[j].innerHTML
}
function deleteCellsByCol(tid){
    var s="";
    var tObj=document.getElementById(tid);
    for(var i=0; i<tObj.rows.length; i++){
        if(tObj.rows[i]!=null){
            for(var j in tObj.rows[i].cells){
                if(tObj.rows[i].cells[j].innerHTML){
                    for(var k = 1; k < tObj.rows[i].cells[j].colSpan; k++){
                        tObj.rows[i].deleteCell(parseInt(j) + 1);
                    }
                }
            }
        }
    }
}
function deleteCellsByRow_bad(tid){
    var deletedCount = 0;
    var tObj=document.getElementById(tid);
    for(var i=0; i<tObj.rows.length; i++){
        if(tObj.rows[parseInt(i)+1]){
            for(var j in tObj.rows[i].cells){
                rowSpanCount = tObj.rows[i].cells[j].rowSpan;
                if(rowSpanCount > 1){
                    for(var k in tObj.rows[parseInt(i)+1].cells){
                        if(tObj.rows[i].cells[j].innerHTML == tObj.rows[parseInt(i)+1].cells[k].innerHTML){
                            tObj.rows[parseInt(i)+1].deleteCell(k);
                        }
                    }
                }
            }
        }
    }
}

function deleteCellsByRow(tid){
    var deletedCount = 0;
    var tObj=document.getElementById(tid);
	var rc = tObj.rows.length; // row count
	var cc = tObj.rows[1].cells.length; // col count // first line is head

	for(var j=cc-1; j >= 0; j--) {
		for(var i=1; i<rc; i++) {
			if(tObj.rows[i].cells.length >= j) {
				if(tObj.rows[i].cells[j]) {
					var rowSpanCount = tObj.rows[i].cells[j].rowSpan;
					for(var k=1; k<rowSpanCount; k++) {
						tObj.rows[i+k].deleteCell(j);

					}
				}
			}
		}
	}
/*
    for(var i=0; i<tObj.rows.length; i++){
        if(tObj.rows[parseInt(i)+1]){
            for(var j=tObj.rows[i].cells.length; j >0; j--){
                rowSpanCount = tObj.rows[i].cells[j].rowSpan;
                if(rowSpanCount > 1){
                    for(var k in tObj.rows[parseInt(i)+1].cells){
                        if(tObj.rows[i].cells[j].innerHTML == tObj.rows[parseInt(i)+1].cells[k].innerHTML){
                            tObj.rows[parseInt(i)+1].deleteCell(k);
                        }
                    }
                }
            }
        }
    }
*/
}
////////// merge


// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});