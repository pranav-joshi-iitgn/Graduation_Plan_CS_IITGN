import pandas as pd
Courses = pd.read_csv("Courses.tsv",sep='\t')
Used_courses = []
course_codes:pd.Series = Courses["Course No"]
short_courses = course_codes.str.startswith("SC")
Courses.where(~short_courses,inplace=True)
Courses.dropna(how="all",inplace=True)
course_codes:pd.Series = Courses["Course No"]
course_credits:pd.Series = Courses["Credit"]
total_credits = course_credits.sum()
print("Total credits",int(total_credits))
MC = {}
MC["HSS"] = ["HS 191","HS 192","HS 151","HS 221","HS 201"]
MC["Maths"] = ["MA 103","MA 104","MA 203"]
MC["common"] = ["FP 100","ES 101","ES 112","ES 113","ES 114","ES 115","ES 116","ES 117","ES 243","BS 192",]
MC["CS"] = ["ES 242(N)","ES 214","ES 204","ES 215","CS 201","CS 330","CS 202","CS 329","CS 331"]
MC["Viva Voce"] = [f"IN 10{x}" for x in range(1,9)]
MC["PE"] = ["PE 101 A","PE 101 B"] + [f"PE 10{x}" for x in range(2,5)]
def check_mandatory(L:list[str],course_type:str):
    good = True
    for code in L:
        if not code in course_codes.values:
            print("NEED to do",code)
            good = False
        else:Used_courses.append(code)
    if good:print("All manadatory",course_type,"courses done")
for course_type,L in MC.items():check_mandatory(L,course_type)
def get_credits_with_code(code:str,return_codes=False):
    courses = course_codes.str.startswith(code)
    codes = course_codes.values[courses.values]
    Used_courses.extend(codes)
    cred = course_credits.values[courses.values]
    if return_codes: return int(cred.sum()),codes
    return int(cred.sum())
def get_credits_with_basket(basket:list[str],return_codes=False):
    courses = course_codes.isin(basket)
    codes = course_codes.values[courses.values]
    Used_courses.extend(codes)
    cred = course_credits.values[courses.values]
    if return_codes: return int(cred.sum()),codes
    return int(cred.sum())
GE_cred,GE_courses = get_credits_with_code("GE",True)
HS_cred,HS_courses = get_credits_with_code("HS",True)
MS_cred,MS_courses = get_credits_with_code("MS",True)
DES_cred,DES_courses = get_credits_with_code("DES",True)
print("GE credits",GE_cred,":",', '.join(GE_courses))
print("HS credits",HS_cred,":",', '.join(HS_courses))
print("MS credits",MS_cred,":",', '.join(MS_courses))
print("DES credits",DES_cred,":",', '.join(DES_courses))
total_hss_credits = int(GE_cred+HS_cred+MS_cred+DES_cred)
print("Total humanities credits",total_hss_credits,'/ 28')
if total_hss_credits < 28 : print("NEED to do more humanities courses")
if GE_cred < 4 : print("NEED to do more General Education courses")

Baskets = {"Materials":3,"Science":8,"Mathematics":2,"Algorithms":8,"Systems":8}
Basket_credits = {}
for Basket,min_creds in Baskets.items():
    b = pd.read_csv(f'Baskets/{Basket}.csv')["Course Code"].values
    b,codes = get_credits_with_basket(b,True)
    print(f"{Basket} Basket credits:",b,"/",min_creds,":",", ".join(codes))
    if b < min_creds: print("NEED to do more courses from",Basket,"Basket")
    Basket_credits[Basket] = b

# TODO: Basket for BS courses
# BS_creds = get_credits_with_code("BS") - 3 # removing UGSL
# BS_creds = (max(Basket_credits["Science"]-8,0)+BS_creds)
# print("BS credits:",BS_creds)
# if BS_creds < 4: print("NEED to do more BS courses")

projects = course_codes.str.endswith("99").values
project_codes = course_codes.values[projects]
Used_courses.extend(project_codes)
cs_projects = course_codes.str.startswith("CS").values & projects
project_cred = min(int(course_credits.values[projects].sum()),16)
cs_project_cred = int(course_credits.values[cs_projects].sum())
print("Total Project Credits",project_cred,'/ 4 (Open Project Course) :',", ".join(project_codes))
print("CS Project Credits",cs_project_cred)

# open project
if project_cred < 4 : print("NEED to do an open project")
else: cs_project_cred = min([project_cred-4,cs_project_cred,8])
print("CS Project Credits counted as Discipline Elective:",cs_project_cred)
b = pd.read_csv(f'CS_elective.csv')["Course Code"].values
cs_elect_cred = get_credits_with_basket(b) + cs_project_cred
print(f"CS elective credits:",cs_elect_cred,'/ 26')
if cs_elect_cred < 26: print("NEED to do more CS electies")

Extra = (
      max(total_hss_credits - 28,0)
    + sum((max(Basket_credits[x]-Baskets[x],0) for x in ["Materials","Science","Mathematics"]))
    + max(cs_elect_cred-26,0)
)

print("Extra credits:",Extra)

Used_courses = list(set(Used_courses))
Used_courses = course_codes.isin(Used_courses)
Unused_courses = ~ Used_courses
Used_courses = Courses.where(Used_courses).dropna(how='all')
Unused_courses = Courses.where(Unused_courses).dropna(how='all')
# print("Courses considered:")
# print(Used_courses.loc[:,["Course No","Course Name"]])
print("Courses not considered:")
print(Unused_courses.loc[:,["Course No","Course Name","Credit"]])

