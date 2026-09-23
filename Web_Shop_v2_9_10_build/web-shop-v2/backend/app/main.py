import os,hashlib,secrets
from datetime import datetime,timedelta,timezone
from typing import Optional
import jwt,httpx
from fastapi import FastAPI,Depends,HTTPException,Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,EmailStr
from sqlalchemy import create_engine,String,DateTime,Text,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker,Session

DATABASE_URL=os.getenv('DATABASE_URL','postgresql+psycopg://webshop:webshop@localhost:5432/webshop');JWT_SECRET=os.getenv('JWT_SECRET','dev-only-change-me');OPENROUTER_KEY=os.getenv('WEBNOR_OPENROUTER_KEY','');OPENROUTER_BASE=os.getenv('OPENROUTER_BASE_URL','https://openrouter.ai/api/v1')
engine=create_engine(DATABASE_URL,pool_pre_ping=True);SessionLocal=sessionmaker(engine,expire_on_commit=False)
class Base(DeclarativeBase): pass
class User(Base):
 __tablename__='users';id:Mapped[int]=mapped_column(primary_key=True);name:Mapped[str]=mapped_column(String(120));email:Mapped[str]=mapped_column(String(255),unique=True,index=True);password_hash:Mapped[str]=mapped_column(String(255));business_name:Mapped[Optional[str]]=mapped_column(String(255),nullable=True);role:Mapped[str]=mapped_column(String(30),default='user');doom_plan:Mapped[Optional[str]]=mapped_column(String(50),nullable=True);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
class Contact(Base):
 __tablename__='contact_inquiries';id:Mapped[int]=mapped_column(primary_key=True);name:Mapped[str]=mapped_column(String(120));email:Mapped[str]=mapped_column(String(255));company:Mapped[Optional[str]]=mapped_column(String(255),nullable=True);intent:Mapped[str]=mapped_column(String(80));message:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
class WebnorLog(Base):
 __tablename__='webnor_usage';id:Mapped[int]=mapped_column(primary_key=True);message:Mapped[str]=mapped_column(Text);path:Mapped[Optional[str]]=mapped_column(String(255),nullable=True);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
Base.metadata.create_all(engine)
app=FastAPI(title='Web Shop API',version='2.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:3000','http://127.0.0.1:3000'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class Signup(BaseModel): name:str;email:EmailStr;password:str;business_name:Optional[str]=None
class Login(BaseModel): email:EmailStr;password:str
class ContactIn(BaseModel): name:str;email:EmailStr;company:Optional[str]=None;intent:str;message:str
class WebnorIn(BaseModel): message:str;session_id:Optional[str]=None;page_context:Optional[str]=None

def pw(v): return hashlib.pbkdf2_hmac('sha256',v.encode(),b'web-shop-v2',180000).hex()
def token(u:User): return jwt.encode({'sub':str(u.id),'role':u.role,'exp':datetime.now(timezone.utc)+timedelta(hours=12)},JWT_SECRET,algorithm='HS256')
def current(auth:Optional[str]=Header(default=None,alias='Authorization')):
 if not auth or not auth.startswith('Bearer '): raise HTTPException(401,'Authentication required')
 try: p=jwt.decode(auth[7:],JWT_SECRET,algorithms=['HS256'])
 except jwt.PyJWTError: raise HTTPException(401,'Invalid or expired token')
 with SessionLocal() as db:
  u=db.get(User,int(p['sub']))
  if not u: raise HTTPException(401,'User not found')
  return u
@app.get('/api/health')
def health(): return {'status':'online','service':'web-shop','version':'2.0.0'}
@app.post('/api/auth/signup')
def signup(x:Signup):
 with SessionLocal() as db:
  if db.scalar(select(User).where(User.email==x.email)): raise HTTPException(409,'An account with this email already exists.')
  u=User(name=x.name,email=x.email,password_hash=pw(x.password),business_name=x.business_name);db.add(u);db.commit();return {'ok':True,'message':'Account created'}
@app.post('/api/auth/login')
def login(x:Login):
 with SessionLocal() as db:
  u=db.scalar(select(User).where(User.email==x.email))
  if not u or u.password_hash!=pw(x.password): raise HTTPException(401,'Email or password is incorrect.')
  return {'access_token':token(u),'token_type':'bearer','role':u.role,'doom_plan':u.doom_plan}
@app.get('/api/profile')
def profile(u:User=Depends(current)): return {'id':u.id,'name':u.name,'email':u.email,'business_name':u.business_name,'role':u.role,'doom_plan':u.doom_plan}
@app.post('/api/contact')
def contact(x:ContactIn):
 with SessionLocal() as db: db.add(Contact(**x.model_dump()));db.commit()
 return {'ok':True,'message':'Received. We will respond with clear next steps.'}

async def webnor_ai(message:str,path:str):
 if not OPENROUTER_KEY:return None
 system='''You are Webnor, the Web Shop website guide. Explain Web Shop, DOOM AI, its capabilities, services, process, contact paths and public website navigation. You are not DOOM. Do not access private client data. Do not perform business analysis. Keep answers concise and premium. If asked something unrelated, redirect to Web Shop.'''
 try:
  async with httpx.AsyncClient(timeout=18) as c:
   r=await c.post(OPENROUTER_BASE+'/chat/completions',headers={'Authorization':f'Bearer {OPENROUTER_KEY}','Content-Type':'application/json'},json={'model':'openai/gpt-4.1-mini','messages':[{'role':'system','content':system},{'role':'user','content':message}]})
   if r.is_success:return r.json()['choices'][0]['message']['content']
 except Exception: return None
 return None
@app.post('/api/webnor/chat')
async def webnor(x:WebnorIn):
 m=x.message.lower();reply=await webnor_ai(x.message,x.page_context or '/')
 actions=[]
 if reply is None:
  if 'doom' in m: reply='DOOM is Web Shop’s flagship command-layer intelligence product. It spans six powers: Business Management, Website Management, Content Intelligence, Predictive Intelligence, Founder Workflow and Private Intelligence.';actions=[{'label':'Explore DOOM','action':'/doom'}]
  elif 'service' in m or 'integration' in m: reply='Web Shop supports Custom Integrations & Onboarding, Premium Website Development, Branding & Design Systems, Advanced Analytics, Custom Feature Development and ongoing Growth & Operational Partnership.';actions=[{'label':'View services','action':'/services'}]
  elif 'contact' in m or 'start' in m or 'access' in m: reply='Use Contact to request a conversation, ask about DOOM early access or submit a project inquiry.';actions=[{'label':'Contact Web Shop','action':'/contact'}]
  elif 'private' in m: reply='DOOM includes a Private Intelligence concept for sensitive work through a local processing path. Private mode should not silently fall back to cloud processing.';actions=[{'label':'See Private Intelligence','action':'/capabilities/private-intelligence'}]
  else: reply='I focus on Web Shop, DOOM AI, its capabilities, services and navigation. Tell me what you are exploring and I’ll point you to the right place.'
 with SessionLocal() as db: db.add(WebnorLog(message=x.message,path=x.page_context));db.commit()
 return {'reply':reply,'quick_actions':actions}
@app.get('/api/admin/clients')
def clients(u:User=Depends(current)):
 if u.role!='creator':raise HTTPException(403,'Creator access required')
 with SessionLocal() as db:return [{'id':x.id,'name':x.name,'email':x.email,'role':x.role,'created_at':x.created_at} for x in db.scalars(select(User).order_by(User.id.desc())).all()]
