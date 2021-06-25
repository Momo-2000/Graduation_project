//打开字滑入效果
window.onload = function () {
	$(".connect p").eq(0).animate({ "left": "0%" }, 600);
	$(".connect p").eq(1).animate({ "left": "0%" }, 400);
};


//登录
function judge(){
        var userid = $("input[name='userid']").val();
        var password = $("input[name='password']").val();
        if (userid == "" || password == ""){
            alert("请输入完整信息")}
        else {
            $.post("login",
            {
                'userid' :userid,
                'password' : password,
            },
            function(request){
                if (request.msg == "登录成功!"){
                    alert(request.msg);
                    window.location.href = "/";
                }
                else {
                    $("input[name=password]").focus().val("");
                    alert(request.msg);
                }
        })
        }
}

//注册
function judge_reg(){
        var id = $("input[name='id']").val();
        var username = $("input[name='username']").val();
        var password = $("input[name='password']").val();
        var confirm_password = $("input[name='confirm_password']").val();
        var tel = $("input[name='tel']").val();
        var reg = /^[1][3,4,5,7,8][0-9]{9}$/;
        var sex = $("input[name='sex']").val();
        var age = $("input[name='age']").val();
        var address = $("input[name='address']").val();
        var email = $("input[name='email']").val();
        var major = $("input[name='major']").val();
        var sclass = $("input[name='sclass']").val();

        if (!reg.test(tel)) {
            $("input[name=tel]").focus().val("");
            alert("请输入有效手机号")

        }
        else if (confirm_password!=password){
            $("input[name=confirm_password]").focus().val("");
            alert("两次输入的密码不一致")
        }
        else if (username == "" || password == ""){
            alert("请输入完整信息")}
        else if (sex!="男"&&sex !="女"){
            $("input[name=sex]").focus().val("");
            alert("请明确性别")}
        else {
            $.post("reg",
            {
                'id':id,
                'username' :username,
                'password' : password,
                'tel' :tel,
                'sex' : sex,
                'age' :age,
                'address' : address,
                'email' :email,
                'major' : major,
                'sclass' :sclass,
            },
            function(request){
                if (request.msg == "注册成功!"){
                    alert(request.msg);
                    window.location.href = "/";
                }
                else {
                    $("input[name=password]").focus().val("");
                    alert(request.msg);
                }
        })
        }
}

//修改资料
function judge_infor() {
    var username = $("input[name='nickname']").val();
    var grades = $("input[name='grades']").val();
    var address = $("input[name='address']").val();
    if (username == "" || grades == ""){
        alert("修改个人信息失败，请输入完整信息")}
    else {
        var formData = new FormData();
        formData.append("portrait",$("#avatar_file")[0].files[0]);
        formData.append("username",username);
        formData.append("grades",grades);
        formData.append("address",address);
        $.ajax({
            url : "modify",
            type : 'POST',
            cache : false,
            data : formData,
            processData : false,
            contentType : false,
            success : function(request) {
                if (request.msg == "修改成功!"){
                    alert(request.msg);
                    window.location.href = "/user_data.html";
                }
                else {
                    alert(request.msg);
                }
            }
        });
    //     $.post("modify",
    //     {
    //         'username' :username,
    //         'grades' : grades,
    //         'address':address,
    //
    //     },
    //     function(request){
    //         if (request.msg == "修改成功!"){
    //             alert(request.msg);
    //             window.location.href = "/user_data.html";
    //         }
    //         else {
    //             $("input[name=password]").focus().val("");
    //             alert(request.msg);
    //         }
    // })
    }
}

$("#avatar_file").change(function() { //avatar_file  input[file]的ID
    // 获取上传文件对象
    var file = $(this)[0].files[0];
    // 读取文件URL
    var reader = new FileReader();
    reader.readAsDataURL(file);
    // 阅读文件完成后触发的事件
    reader.onload = function() {
        // 读取的URL结果：this.result
        $("#avatar_img").attr("src", this.result).show(); //avatar_img  img标签的ID
    }
});


//提交每日健康&& healths!="黄"&&healths!="绿"
function judge_health() {
    var userid = $("input[name='userid']").val();
    var grades = $("input[name='grades']").val();
    var major = $("input[name='major']").val();
    var nowaddress = $("input[name='nowaddress']").val();
    var healths = $("input[name='healths']").val();
    var potential1 = $("input[name='potential1']:checked").val();
    var potential2 = $("input[name='potential2']:checked").val();
    var temperature = $("input[name='temperature']").val();
    var tel = $("input[name='tel']").val();
    var reg = /^[1][3,4,5,7,8][0-9]{9}$/;
    if (grades==""||major==""||nowaddress==""||healths==""||temperature==""){
        alert("请完善信息！")
    }
    else if(parseInt(temperature)<33|| parseInt(temperature)>40){
        alert("请输入实际体温！")
    }
    else if (!reg.test(tel)) {
        $("input[name=tel]").focus().val("");
        alert("请输入有效手机号！")
    }
    else if (healths!="红" && healths!="绿" && healths!="黄"){
        $("input[name=healths]").focus().val("");
        alert("健康状态有误！");
    }
    else {
        var formData = new FormData();
    formData.append("userid",userid);
    formData.append("major",major);
    formData.append("healths",healths);
    formData.append("nowaddress",nowaddress);
    formData.append("potential1",potential1);
    formData.append("potential2",potential2);
    formData.append("grades",grades);
    formData.append("temperature",temperature);
    formData.append("tel",tel);
    $.ajax({
        url : "jiankang",
        type : 'POST',
        cache : false,
        data : formData,
        processData : false,
        contentType : false,
        success : function(request) {
            if (request.msg == "打卡成功!"){
                alert(request.msg);
                window.location.href = "/";
            }
            else if (request.status == "-2"||request.status == "-3"){
                alert(request.msg);
                window.location.href = "/";
            }
            else {
                alert(request.msg);
            }
        }
    });
    }

}

//外出请假
function judge_leave() {
    var userid = $("input[name='userid']").val();
    var username = $("input[name='username']").val();
    var tel = $("input[name='tel']").val();
    var reg = /^[1][3,4,5,7,8][0-9]{9}$/;
    var outreason = $("input[name='outreason']").val();
    var outaddress = $("input[name='outaddress']").val();
    var outtime = $("input[name='outtime']").val();
    var intime = $("input[name='intime']").val();

    if (!reg.test(tel)) {
        $("input[name=tel]").focus().val("");
        alert("请输入有效手机号")
    }
    else {
        var formData = new FormData();
        formData.append("userid",userid);
        formData.append("username",username);
        formData.append("tel",tel);
        formData.append("outreason",outreason);
        formData.append("outaddress",outaddress);
        formData.append("outtime",outtime);
        formData.append("intime",intime);

        $.ajax({
            url : "waichu",
            type : 'POST',
            cache : false,
            data : formData,
            processData : false,
            contentType : false,
            success : function(request) {
                if (request.status=="0"){
                    alert(request.msg);
                    window.location.href = "/";
                }
                else if (request.status == "-2"||request.status == "-3"){
                    alert(request.msg);
                    window.location.href = "/";
                }
                else {
                    alert(request.msg);
                }
            }
        });
    }

}


$("#avatar_file").change(function() { //avatar_file  input[file]的ID
    // 获取上传文件对象
    var file = $(this)[0].files[0];
    // 读取文件URL
    var reader = new FileReader();
    reader.readAsDataURL(file);
    // 阅读文件完成后触发的事件
    reader.onload = function() {
        // 读取的URL结果：this.result
        $("#avatar_img").attr("src", this.result).show(); //avatar_img  img标签的ID
    }
});


//未打卡显示
function signin_show() {
    $('#no_signinS').css('display','none');
    $('#no_signinV').css('display','inline-table');
    $('#baobeiS').css('display','none');
    $('#baobeiV').css('display','inline-table');
}

function signin_back() {
    $('#no_signinS').css('display','inline-table');
    $('#no_signinV').css('display','none');
    $('#baobeiS').css('display','inline-table');
    $('#baobeiV').css('display','none');
}


function submit_tongzhi() {
    var notice_title = $("textarea[name='tz_title']").val();
    var notice_com = $("textarea[name='tz_comment']").val();
    var formData = new FormData();
    formData.append("notice_title",notice_title);
    formData.append("notice_com",notice_com);

        $.ajax({
            url : "notice",
            type : 'POST',
            cache : false,
            data : formData,
            processData : false,
            contentType : false,
            success : function(request) {
                if (request.status=="0"){
                    alert(request.msg);
                    window.location.href = "/";
                }
                else {
                    alert(request.msg);
                }
            }
        });
}






