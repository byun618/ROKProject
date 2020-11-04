# ROKProject

## 목차
[1. 프로젝트 개요](#프로젝트-개요)  
[2. 개발 환경](#개발-환경)  
[3. 개발 파트](#개발-파트)     
[4. 개발 과정](#개발-과정)       
[5. Getting Started](#Getting-Started)  
[6. 기타 링크](#기타-링크) 

## 프로젝트 개요 (2020.07)
* **개요**  
스크린샷을 이미지 인식을 통해 Excel 파일로 변환해준다.
* **장르**  
Game Util Program
* **소개**   
[Rise Of Kingdom](https://roc.lilithgames.com/en)이라는 게임에는 연맹 단위로 사람이 모이고, 그 인원을 관리해야하는 경우가 생긴다. 

<img width="600" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98066669-048c4d80-1e9b-11eb-8ad0-0f725e75376a.PNG">

그 경우에 이런 개인 스탯 정보를 가지고 관리를 하는데, 문제는 하나의 연맹에는 120에서 140여명의 사람들이 모여있다. 이것을 일일히 수작업으로 Excel 파일에 타이핑을 하게되면 시간이 오래 걸리는(2,3시간)것은 물론이고 눈과 손가락 등 피로감이 쌓이게 된다.     
또한, 이 게임에는 서버전이 존재한다. 상대 서버의 전력을 알아야 한다. 
<img width="600" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98066935-c04d7d00-1e9b-11eb-85d7-d69c33a8806f.png">
이 작업도 이러한 서버의 정보를 가지고 Excel 작업을 진행한다. 이것도 상당한 시간이 소요되고 피로도를 동반한다.
시간 소요를 단축하고 피로도를 줄이기 위해 스크린샷을 찍어 이미지를 인식하여 Excel로 변환하는 프로그램을 개발했다.

*여기서는 member_scan에 관해서만 설명.*

## 개발 환경
* Anaconda
    * OpenCV
    * Pandas
* Jupyter Notebook
* Google Cloud Vision

## 개발 내용
* 위에 있는 이미지를 **OpenCV**와 **Pillow** 모듈을  이용하여 이미지를 Crop 및 전처리  
    <img width="200" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071088-f09a1900-1ea5-11eb-91ee-d5733177d9f0.PNG"> <img width="200" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071093-f1cb4600-1ea5-11eb-8f1d-b209a925b556.PNG">  <img width="200" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071087-f0018280-1ea5-11eb-8b5e-dab574096610.PNG">  
    이름 전투력 처치수  
    <img width="200" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071086-eed05580-1ea5-11eb-8b6e-5e91a337f1b6.PNG"> <img width="200" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071092-f132af80-1ea5-11eb-8a91-5b2506df468c.PNG">   
    전사 원조   

    <img width="400" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98071090-f09a1900-1ea5-11eb-8294-30337ff52706.PNG">  

    위 5개 이미지를 합친다

* Google Cloud Platform의 **Cloud Vision**을 이용하여 이미지의 문자, 숫자를 인식
* 나온 문자와 숫자를 후처리하여 **Padas DataFrame**을 이용해 Excel 파일로 변환
    ```
    def detect(self, path, name, power, kill, dead, support):

        char = self.detect_text(path)
        li = self.change_to_list(char)
        
        name.append(li[0])
        power.append(self.change_to_number(li[1]))
        kill.append(self.change_to_number(li[2]))
        dead.append(self.change_to_number(li[3]))
        support.append(self.change_to_number(li[4]))
        
        return name, power, kill, dead, support
    ```
    위 이미지를 인식하여 텍스트를 리스트로 변환
    ```
    def export(self):
        df = pd.DataFrame({'name': self.name,
                            'power':self.power,
                            'kill':self.kill,
                            'dead':self.dead,
                            'support':self.support})
        
        filename = fd.asksaveasfilename(filetypes=[('excel file', 'xlsx')], title='Save file as', initialfile='memberinfo.xlsx')
        df.to_excel(filename)
    ```
    DataFrame으로 변환하여 Excel 파일로 저장한다.

## Getting Started
1. [Google Cloud Platform](https://cloud.google.com/)에서 프로젝트를 생성하고 **Cloud Vision**을 등록해, 인증파일을 발급받는다.

2. Repository clone 한다.
    ```
    git clone https://github.com/byun618/ROKProject.git
    ```
3. Anacaonda Jupyter Notebook 실행, 해당 디렉터리로 이동

4. bin 폴더에 인증파일 복사, 
5. ipad_member_scan.ipynb 실행. 코드 내 main 부분을 수정
    ```
    if __name__ == "__main__":
        root = Tk()
        application = Main(root)
        root.resizable(width=False, height=False)
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="bin/본인의 인증파일 이름.json"

        root.mainloop()
    ```

6. 게임에서 위에 있는 것처럼 스크린샷을 찍어 다음 경로에 복사
    ```
    data/member/origin 
    ```
7. 처음부터 Run 하여 최종적으로 main부분을 실행한다.
<img width="600" alt="ezgif com-gif-maker" src="https://user-images.githubusercontent.com/27637757/98069665-a7949580-1ea2-11eb-83bc-8d71a7f440f3.png">


8. 보여지는 메시지대로 차례대로 **이름**, **전투력**, **처치**, **전사**, **원조** 숫자에 박스를 쳐준다.
<img width="600" alt="ezgif com-gif-maker (1)" src="https://user-images.githubusercontent.com/27637757/98069839-1c67cf80-1ea3-11eb-9c08-abbc2e94faba.png">

9. 맨 왼쪽에 있는 이미지 편집을 클릭
<img width="600" alt="ezgif com-gif-maker (3)" src="https://user-images.githubusercontent.com/27637757/98069850-212c8380-1ea3-11eb-919b-3aee52849d70.png">

10. 그 우측에 있는 이미지 인식을 클릭
<img width="600" alt="ezgif com-gif-maker (3)" src="https://user-images.githubusercontent.com/27637757/98069850-212c8380-1ea3-11eb-919b-3aee52849d70.png">


11. 마지막으로 엑셀로 버튼을 클릭하면
<img width="600" alt="ezgif com-gif-maker (2)" src="https://user-images.githubusercontent.com/27637757/98069846-2093ed00-1ea3-11eb-9948-18d70eb1f1c8.png">
<img width="560" alt="ezgif com-gif-maker (4)" src="https://user-images.githubusercontent.com/27637757/98069852-21c51a00-1ea3-11eb-8448-0fa30d1e24a7.png">
