from blog.models import UserClass
from blog.models import MovieClass

def UserDataSave():
    #部分用户的推荐电影
    Recommand=open('blog/Recommand_Movie.csv','r')
    R_movie=Recommand.readlines()

    for item in R_movie:
        line=item.strip().split('\t',1)
        uid=line[0]
        r_line=line[1]
        User_Class = UserClass(userId=uid,user_Recommand=r_line)
        User_Class.save()
    print(1)
    #部分用户的历史电影
    History=open('blog/History_Movie.csv','r')
    H_movie=History.readlines()
    i=0
    for item in H_movie:
        line = item.strip().split('\t',1)
        uid = line[0]
        h_line = line[1]
        try:
            User_Class=UserClass.objects.get(userId=uid)
            User_Class.user_History = h_line
            User_Class.save()
        except:
            i+=1
    print('error num',i)
    Recommand.close()
    History.close()

def MovieDataSave():
    #2000电影的信息
    MovieData=open('blog/Movie2000.csv','r',encoding='utf-8')
    MovieData.readline()
    all_movie=MovieData.readlines()
    for item in all_movie:
        line=item.strip().split(',',1)
        mid=line[0]
        m_line=line[1]
        Movie_Class=MovieClass(movieId=mid,movie_info=m_line)
        Movie_Class.save()
    #2000电影的src
    fopen=open('blog/2000.json','r').readline()
    movie_picture=eval(fopen)
    print(2)
    i=0
    for key,values in movie_picture.items():
        try:
            Movie_Class = MovieClass.objects.get(movieId=key)
            Movie_Class.movie_src = values
            Movie_Class.save()
        except:
            i+=1
    print('error num',i)
    Movie_Class.save()
    MovieData.close()



