# mSHR Backend
Project BOM의 베트남 학교에서 신체검사 측정을 돕기 위한 웹앱으로 지역별 학교에서 기기를 두고 계측이 끝나면 학생들 정보가 담긴 qr 코드를 통해 입력해서 모든 계측이 끝나면 저장. 또한 관리자 페이지에서 지역, 학교별 학생들 계측의 dashboard 제공.

서버는 EC2, RDS 를 사용하고 분산처리를 위해 ELB-ALB 를 사용하고, 보안을 위해 VPC 안에 EC2를 public subnet 에 두고 RDS 를 private subnet 에 두어 EC2 통해서만 접근이 가능. 
배포는 nGinx gUnicorn 을 사용. 

## mobile_api
학교측 기기 api
* account : 해당 학교 기기 로그인, 토큰 재발급(JWT)
* checkup : 검측 결과 일괄 혹은 개별 업로드
* student : 학생 개별/단체 등록, MIN(주민등록번호) 중복 체크,학생 목록, 검측 기록, 특정 학생 정보 조회

![image](https://user-images.githubusercontent.com/47446855/226415658-a961fdc5-6842-46bf-bdfe-4788fe3a44c2.png)


## admin_api
정부 관리자 페이지 api
* account : 권한 (마스터/도/시/동/학교 지역 계층별 권한) 별 로그인, 계정 설정, 토큰 재발급(JWT)
* area : 도/시/동 조건에 대한 하위 지구 정보 반환
* dashboard : 각 권한별 학생들 신체검사 대시보드 정보 제공, 공지사항
* log : 계정 로그인 후 모든 계정의 로그가 기록되는데 모든 로그 제공 (마스터 권한만 가능)
* notice : 공지사항 열람/추가/파일업로드/상세정보/수정/제거
* school : 관리자 페이지에서 학교 정보 열람/확인/추가/상세정보/수정/제거
* studentHealth_healthCheckup : 학생들의 신체검사 측정 기록을 열람/추가/수정/제거 (bulk 로 가능)
* studentHealth_student : 학생들을 열람/추가/수정/제거 (bulk 로 가능)
* user : 마스터 계정이 그 아래 권한을 가진 계정 생성/수정/제거

![image](https://user-images.githubusercontent.com/47446855/226415583-4bc52c9d-cf3a-45be-8f5d-7f0f5a9c1dc1.png)

