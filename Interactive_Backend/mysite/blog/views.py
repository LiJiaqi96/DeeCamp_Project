from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.shortcuts import render

from blog.DataSave import *
from blog.models import User
from blog.models import UserClass
from blog.models import MovieClass
import json

def RS(request):
    return render_to_response("CreativeWriting.html")

def update(request):
    UserDataSave()
    MovieDataSave()
    return render_to_response("cwrs.html")

def loginc(request):
    un = request.POST.get('username')
    pw = request.POST.get('password')
    #print(un)
    userResult = User.objects.filter(username=un, password=pw)
    if (len(userResult) > 0):
        #return render_to_response('cwrs.html', {'username': un})
        return render_to_response('KGRS2.html', {'username': un})
    else:
        return render_to_response('CreativeWriting.html',{"errors": "Username or password is incorrect!"})

def signupc(request):
    un = request.POST.get('username1')
    em = request.POST.get('email')
    pw1 = request.POST.get('password1')
    pw2 = request.POST.get('password2')

    filterResult = User.objects.filter(username=un)
    if len(filterResult) > 0:
        return render_to_response('CreativeWriting.html', {"errors2": "Username already exists!"})
    else:
        errors = []
        if (pw2 != pw1):
            errors.append("The password entered twice is inconsistent!")
            return render_to_response('CreativeWriting.html', {'errors2': errors})
            # 将表单写入数据库
        user = User()
        user.username = un
        user.password = pw1
        user.email = em
        user.save()
        # 返回注册成功页面
        return render_to_response('CreativeWriting.html', {"errors": "registration success!"})
    return render_to_response('CreativeWriting.html')

def KGRS2(request):
    return render_to_response("KGRS2.html")

@csrf_exempt
def get_info(request):
    uid = request.POST.get('uid')
    #print(uid)
    user_one=UserClass.objects.get(userId=uid)
    movie_recommand=user_one.user_Recommand
    movie_history=user_one.user_History
    re_movie_list=movie_recommand.split('\t')[0:12]
    hi_movie_list=movie_history.split('\t')[0:12]

    highmovie=['3541415', '3742360', '1292052', '1295644', '1652587', '1292720', '1929463', '2131459', '1292215', '1292001']
    popular_list=[]
    recomend_list = []

    itemVo_list = []
    items1 = []
    items2 = []

    for item in highmovie:
        movie_one=MovieClass.objects.get(movieId=item)
        line=movie_one.movie_info.split(',')
        star=( 5*float(line[8])+4*float(line[9])+3*float(line[10])+2*float(line[11])+float(line[12]) )/100
        item={'name':line[0],'img_url':movie_one.movie_src,'star':star,'rating_count':line[7],'mid':movie_one.movieId}
        popular_list.append(item)

    for item in re_movie_list:
        movie_one=MovieClass.objects.get(movieId=item)
        line=movie_one.movie_info.split(',')
        star=( 5*float(line[8])+4*float(line[9])+3*float(line[10])+2*float(line[11])+float(line[12]) )/100
        item={'name':line[0],'img_url':movie_one.movie_src,'star':star,'rating_count':line[7],'mid':movie_one.movieId}
        recomend_list.append(item)

    for item in hi_movie_list[0:6]:
        movie_one = MovieClass.objects.get(movieId=item)
        line = movie_one.movie_info.split(',')
        star = (5 * float(line[8]) + 4 * float(line[9]) + 3 * float(line[10]) + 2 * float(line[11]) + float(line[12])) / 100
        item = {'name': line[0], 'img_url': movie_one.movie_src, 'star': star, 'rating_count': line[7], 'mid': movie_one.movieId}
        items1.append(item)

    for item in hi_movie_list[0:6]:
        movie_one = MovieClass.objects.get(movieId=item)
        line = movie_one.movie_info.split(',')
        star = (5 * float(line[8]) + 4 * float(line[9]) + 3 * float(line[10]) + 2 * float(line[11]) + float(line[12])) / 100
        item = {'name': line[0], 'img_url': movie_one.movie_src, 'star': star, 'rating_count': line[7], 'mid': movie_one.movieId}
        items2.append(item)
    itemVo_list.append(items1)
    itemVo_list.append(items2)

    data1={'uid':uid,'popular_list':popular_list,'recomend_list':recomend_list,'itemVo_list':itemVo_list}
    #print(data1)
    #for item in recomend_list:
    #print(item['img_url'])
    #return HttpResponse(json.dumps(data1), content_type='application/json')
    return render(request,"KGRS2.html",data1)


@csrf_exempt
def get_movie(request):
    uid = request.POST.get('element2')
    mid = request.POST.get('element1')
    mid=mid.replace('/','')
    print(uid,mid)
    movie_one = MovieClass.objects.get(movieId=mid)
    line=movie_one.movie_info.split(',')
    reason=None
    itemVo={'name':line[0],'director':line[1],'scriptwriter':line[2],'players':line[3],'categories':line[4],'country':line[5],'tags':line[6],'language':[13],'recommend_reason':reason}
    data={'itemVo':itemVo}
    print(data)
    #return render(request,'KGRS2.html',data2)
    return HttpResponse(json.dumps(data), content_type='application/json')