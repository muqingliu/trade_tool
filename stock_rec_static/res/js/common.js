<!--
function forMenuHover()
{
    jQuery('#nav-menu > li').hover(
        function()
        {
            jQuery(this).addClass('mega-hover');
            jQuery(this).children('div').children('.sub').stop(true, true).fadeIn(1);

        },function()
        {
            jQuery(this).removeClass('mega-hover');
            jQuery(this).children('div').children('.sub').stop(true, true).slideUp(1);
        }
    );
}

function checkIE6()
{
	if(jQuery.browser.msie && $.browser.version < 7)
	{
		return true;
	}
	else
		return false;
}


jQuery(document).ready(
    function()
    {		
        forMenuHover();
			
    }
);


jQuery(document).ready(function(){
    var strUrl = window.location.href;
    var arrUrl = strUrl.split("/");
    var _page = arrUrl[arrUrl.length-1];
    arrUrl = _page.split("?");
    _page = arrUrl[0];

    for (x = 1; x < 10; x++){
        var urls = "";
        switch(x)
        {
           case 1:
             urls = "home.aspx";
             break;
           case 2:
             urls = "pe.aspx,pb.aspx,roe.aspx,g.aspx";
             break;
           case 3:
             urls = "s_jibenxinxi.aspx,s_nianbao.aspx,s_nianbao_leijilv.aspx,s_nianbao_jinliuqilv.aspx,s_nianbao_full.aspx,s_zhongbao.aspx,s_zhongbao_leijilv.aspx,s_zhongbao_jinliuqilv.aspx,s_zhongbao_full.aspx";
             break;
           case 4:
             urls = "l_fenzutongji.aspx,l_fenzuleiji.aspx,l_fenzutongji_d.aspx,l_fenzutongji_b.aspx";
             break;
           case 5:
             urls = "b_zengzhanglv.aspx,b_dubang_roa_roe.aspx,b_dubang_jinglirun.aspx,b_dubang_zhouzhuanlv.aspx,b_guzhibijiao.aspx,b_zhuyaozichan.aspx,b_fuzhaijiegou.aspx,b_zengzhanglv_g.aspx,b_zengzhanglv_b.aspx,b_dubang_roa_roe_g.aspx,b_dubang_roa_roe_b.aspx,b_dubang_jinglirun_g.aspx,b_dubang_jinglirun_b.aspx,b_dubang_zhouzhuanlv_g.aspx,b_dubang_zhouzhuanlv_b.aspx,b_zhuyaozichan_g.aspx,b_zhuyaozichan_b.aspx,b_fuzhaijiegou_g.aspx,b_fuzhaijiegou_b.aspx,b_t.aspx";
             break;
           case 6:
             urls = "kuaimanyuekan.aspx";
             break;
           case 8:
             urls = "contact.aspx";
             break;
           default:
             urls = "";
        }
        var s = urls.split(",");
        for (i = 0; i < s.length; i++){
            if (s[i] == _page){
                $("#im531_" + x).addClass("selected");
                return;
            }
        }
    }

});




///
function killErrors(){return true;} 
//window.onerror = killErrors;
//-->