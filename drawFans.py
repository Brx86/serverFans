import os, csv, time, requests, asyncio, aiohttp
from pyecharts import options as opts
from pyecharts.charts import Page, Pie


class Proxy:
    def __init__(self):
        self.session = requests.Session()

    def get(self, t=1):
        proxyUrl = [
            "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=17295e416bb52260d9a94770f10dfbed&orderNo=GL202108231518565rnpfk2x&count=1&isTxt=0&proxyType=1",
            "http://pandavip.xiongmaodaili.com/xiongmao-web/apiPlus/vgl?secret=17295e416bb52260d9a94770f10dfbed&orderNo=VGL20210902224903WTH4fq5d&count=1&isTxt=0&proxyType=1&validTime=0&removal=1&cityIds=",
        ]
        while 1:
            try:
                p = self.session.get(proxyUrl[t]).json()
                # if p["code"]:
                #    print("请勿重复提取！")
                #    return
                ipPort = f"{p['obj'][0]['ip']}:{p['obj'][0]['port']}"
                proxies = {"http": f"http://{ipPort}", "https": f"http://{ipPort}"}
                print(f"Trying {ipPort}...", end="")
                r = self.session.get(
                    "https://api.bilibili.com", proxies=proxies, timeout=5
                )
                print("True! ")
                return f"http://{ipPort}"
            except KeyboardInterrupt:
                time.sleep(0.5)
                print("KeyboardInterrupt, do not use proxy")
                return
            except:
                print(" Proxy failed, changing...")
            time.sleep(0.8)

    def times(self, t=1):
        timesApi = [
            "http://www.xiongmaodaili.com/xiongmao-web/api/leftCount?type=1&orderNo=GL202108231518565rnpfk2x",
            "http://www.xiongmaodaili.com/xiongmao-web/api/leftCount?type=15&orderNo=VGL20210902224903WTH4fq5d",
        ]
        times = self.session.get(timesApi[t]).json()["obj"]
        print(f"Api {t} remains {times} times")

    def t(self, t=1):
        timesApi = [
            "http://www.xiongmaodaili.com/xiongmao-web/api/leftCount?type=1&orderNo=GL202108231518565rnpfk2x",
            "http://www.xiongmaodaili.com/xiongmao-web/api/leftCount?type=15&orderNo=VGL20210902224903WTH4fq5d",
        ]
        times = requests.get(timesApi[t]).json()["obj"]
        return times

class Spyder:
    def __init__(self, mid, proxy=0):
        self.proxy = Proxy().get()
        self.mid = str(mid)
        self.session = requests.Session()
        self.getName()

    def getName(self):
        userApi = f"https://api.bilibili.com/x/web-interface/card?mid={self.mid}"
        up = self.session.get(userApi).json()["data"]
        self.upName = up["card"]["name"]
        self.upFans = int(up["follower"])
        if self.upFans < 250:
            self.upPages = int(self.upFans) // 50 + 1
        else:
            self.upPages = 5

    def getFans(self, pn):
        print(f"Page {pn+1}...")
        fansApi = (
            f"http://api.bilibili.com/x/relation/followers?vmid={self.mid}&pn={pn+1}"
        )
        return self.session.get(fansApi).json()["data"]["list"]

    async def getInfo(self, client, u):
        userApi = f"http://api.bilibili.com/x/space/acc/info?mid={u['mid']}&jsonp"
        r = await client.get(userApi, proxy=self.proxy)
        try:
            ui = await r.json()
            ui = ui["data"]
        except:
            return
        print(f"UID: {u['mid']}\tLevel: {ui['level']}")
        with open(f"{self.mid}/{self.upName}.csv", "a+") as f:
            wCsv = csv.writer(f)
            wCsv.writerow(
                [
                    u["mid"],
                    u["mtime"],
                    u["uname"],
                    u["vip"]["vipType"],
                    ui["level"],
                    ui["sex"],
                    u["sign"].replace("\n", " "),
                ]
            )

    def draw(self):
        sumUsers = 0
        lvList = [[f"lv{x}", 0] for x in range(7)]
        with open(f"{self.mid}/{self.upName}.csv", "r") as f:
            rCsv = csv.reader(f)
            for line in rCsv:
                lv = line[4]
                if not line[4].isdigit():
                    continue
                lv = int(lv)
                sumUsers += 1
                lvList[lv][1] += 1
        for u in range(7):
            lvList[u][1] = round(100 * lvList[u][1] / sumUsers, 2)
        tTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 30))
        pie = (
            Pie()
            .add("", lvList, radius=["30%", "70%"], center=["55%", "50%"])
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{self.upName} 粉丝等级占比",
                    subtitle=f"最后更新于: {tTime}\n\n样本数: {sumUsers}/{self.upFans}\n\nUID: {self.mid}",
                    pos_left="15%",
                ),
                legend_opts=opts.LegendOpts(
                    orient="vertical", pos_top="30%", pos_left="15%"
                ),
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}%"))
        )
        pie.render(f"{self.mid}/index.html")
        print("Chart Generated!")

    async def main(self):
        uList = []
        if not os.path.exists(self.mid):
            os.mkdir(self.mid)
        with open(f"{self.mid}/{self.upName}.csv", "w+") as f:
            f.write("uid,mtime,uname,vipType,level,sex,sign\n")
        for i in range(self.upPages):
            uList.extend(self.getFans(i))
        async with aiohttp.ClientSession() as client:
            tasks = [self.getInfo(client, u) for u in uList]
            await asyncio.gather(*tasks)
        print(f"{self.upName} Finished！")
        self.draw()

    def run(self):
        Proxy().times()
        start = time.time()
        asyncio.run(self.main())
        print(f"Cost {time.time()-start} secs")
        Proxy().times()


if __name__ == "__main__":
    Spyder("1").run()
