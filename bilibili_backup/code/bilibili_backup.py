import os
from ffmpy3 import FFmpeg
import tkinter as tk
from tkinter.filedialog import askdirectory 
 

#设计一个开罐器，打开目标文件夹后生成列表并清理'._'项
class revealer:
    def op(self,path):
        if os.path.isdir(path):
            clist=os.listdir(path)
            clist=[i.strip('._') for i in clist if(len(str(i).strip('._')))!=0]
            clist=list(set(clist))
            return clist
            

    #通过列表项得到下一层文件列表
    def dp(self,path,item):
        path=path+"/"+item
        if os.path.isdir(path):
            nlist=os.listdir(path)
            nlist=[i.strip('._') for i in nlist if(len(str(i).strip('._')))!=0]
            nlist=list(set(nlist))
            return nlist
        else:
            return []





class dispatcher:

    def __init__(self):
        self.source="/Volumes/Element-I/bilibili/源文件"
        self.target="/Volumes/Element-I/bilibili/待存"
        self.list=[]
        # print("缓存池："+self.source+"\n"+"视频池："+self.target)


    def set_path(self,path):
        self.source=path[0]
        self.target=path[1]

    def task_scanner(self,revealer):

        #扫描缓存区部分：
        #清理sourcelist： source_list包含'._文件',及源文件列表txt文件
        #移除._文件
        slist=revealer.op(self.source)
        #移除txt文件
        if '源文件列表.txt' in slist:
            slist.remove('源文件列表.txt')
        if 'DS_Store' in slist:
            slist.remove('DS_Store')
    
        #书写源文件列表.txt文件，换行
        def line_feed(ele):
            return ele+'\n'
        slist_lf=list(map(line_feed,slist))
        slist_path=self.source+'/'+'源文件列表.txt'
        sl = open(slist_path,'w')
        sl.write("".join(slist_lf))   
    
        #扫描已完成列表
        record_path=self.target+"/"+"records.txt"
        #判断records是否存在，不存在则创建
        if not os.path.exists(record_path):
            new=open(record_path,"w")
            new.close()
        records=open(record_path)
        rlist=records.readlines()
        #去除转义字符
        rlist=[i.strip() for i in rlist if(len(str(i).strip()))!=0]
        #从sl中删除rl中的序列
        def tcheck(n):
            return n not in rlist
        tasklist=filter(tcheck,slist)
        self.list=list(tasklist)




    #扫描缓存文件结构,针对list中项
    def cahe_structure(self,seq,dispatcher,revealer):

        #需要先实例化一个dispatcher
        video_path=dispatcher.source+"/"+seq
        #需要先实例化一个revealer
        list1=revealer.op(video_path)
        cache_list_final=[]
        cache_list=[]
        for f1 in list1:
            cache_name=seq+"_"+f1
            cache_path=video_path+"/"+f1
            list2=revealer.op(cache_path)
            for f2 in list2:
                cache_path_d=cache_path+"/"+f2
                if os.path.isdir(cache_path_d):
                    list3=revealer.op(cache_path_d)
                    cache_path=cache_path_d

                    if 'entry.json' in list3:
                        for f3 in list3:
                            cache_path_d=cache_path_d+"/"+f3
                            if os.path.isdir(cache_path_d): 
                                list3=revealer.op(cache_path_d)
                    
                    
                    if '0.blv' in list3:
                        cache_type=1
                    elif 'audio.m4s' in list3:
                        cache_type=2

                    cache_profile=(cache_name,cache_path,cache_type)    
                    cache_list.append(cache_profile)
                    
            cache_list_final.extend(cache_list)



 

        #返回该seq下的缓存列表
        return cache_list_final




def transcoder(video_name,cache_path,cache_type,dispatcher):

    if not os.path.exists(dispatcher.target+'/'+video_name+'.mp4'):
        #blv格式
        if cache_type==1:
            print('转码blv格式文件')
            trans_blv=FFmpeg(inputs={cache_path+'/'+'0.blv':None},
                            outputs={dispatcher.target+'/'+video_name+'.mp4':None})
            trans_blv.run()

        elif cache_type==2:
            print('转码m4s格式文件') 
            trans_m4s=FFmpeg(inputs={cache_path+'/'+'video.m4s':None,cache_path+'/'+'audio.m4s':None},
                            outputs={dispatcher.target+'/'+video_name+'.mp4':None})
            trans_m4s.run()


def core_process(path_data):

    if not path_data == []:

        r=revealer()
        d=dispatcher()
        d.set_path(path_data)
        d.task_scanner(r)
        print('\n',"核心进程获取任务列表","<line148>",'\n',d.list,'\n')

        for t in d.list:
            cache_list_final=d.cahe_structure(t,d,r)
            print("核心进程获取缓存文件列表","<line158>",'\n',cache_list_final[0],'\n')

            for v in cache_list_final:
                print(v[0],"开始")
                
                #执行转码命令
                transcoder(v[0],v[1],v[2],d)

                print(v[0],"完成")

            v_record=t+'\n'
            rla_path=d.target+'/'+'records.txt'
            rla= open(rla_path,'a')
            rla.write(v_record)
            rla.close()


    else:
        print(path_data,"failed")    



def main():


    def selectpath(n):
        path_=askdirectory()
        if n==1:
            path1.set(path_)
            #print(path)
        else:
            path2.set(path_)

    def quit(n):
        if n==1:
            #从StringVar提取变量
            path_s=path1.get()
            path_t=path2.get()
            if os.path.isdir(path_s) and os.path.isdir(path_t):
                path_data=(path_s,path_t)
                print("窗口获得路径","<line212>",'\n','缓存池：'+path_data[0]+'\n'+'视频池：'+path_data[1],'\n')
                core_process(path_data)
            Path.destroy()





    Path=tk.Tk()
    Path.title('B站文件转存')
    path_data=[]
    #路径变量
    path1=tk.StringVar()
    path2=tk.StringVar()
 

    screenwidth = Path.winfo_screenwidth()
    screenheight = Path.winfo_screenheight()
    # 窗口的大小
    width = 345
    height = 150
    # 设置窗口在屏幕居中
    location = "%dx%d+%d+%d" % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    Path.geometry(location)


    Path.rowconfigure(0,weight=1)
    tk.Label(Path,text="源文件池:").grid(row=0,column=0)
    tk.Entry(Path,textvariable=path1).grid(row=0,column=1)
    tk.Button(Path,text="路径选择",command=lambda:selectpath(1)).grid(row=0,column=2)


    Path.rowconfigure(1,weight=1)
    tk.Label(Path,text="目标文件池:").grid(row=1,column=0)
    tk.Entry(Path,textvariable=path2).grid(row=1,column=1)
    tk.Button(Path,text="路径选择",command=lambda:selectpath(2)).grid(row=1,column=2)

    Path.rowconfigure(2,weight=1)
    tk.Button(Path,text="确定",command=lambda:quit(1)).grid(row=2,column=1)
    Path.rowconfigure(3,weight=1)
    tk.Button(Path,text="取消",command=lambda:quit(2)).grid(row=3,column=1)

    Path.rowconfigure(4,weight=1)
    tk.Label(Path,text="=====================================").grid(row=4,column=0,columnspan=3)
    

    Path.mainloop()


if __name__=="__main__":
    main()
    print("Finish!")

    
