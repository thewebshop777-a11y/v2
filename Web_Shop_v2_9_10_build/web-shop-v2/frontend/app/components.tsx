'use client';
import Link from 'next/link';
import {useEffect,useRef,useState} from 'react';
export function Reveal({children,className='' }:{children:React.ReactNode,className?:string}){const r=useRef<HTMLDivElement>(null);useEffect(()=>{const o=new IntersectionObserver(([e])=>{if(e.isIntersecting){e.target.classList.add('is-visible');o.disconnect()}},{threshold:.12});if(r.current)o.observe(r.current);return()=>o.disconnect()},[]);return <div ref={r} className={'reveal '+className}>{children}</div>}
export function MagneticButton({href,children,kind='solid'}:{href:string,children:React.ReactNode,kind?:'solid'|'ghost'}){const [hot,setHot]=useState(false);return <Link onMouseEnter={()=>setHot(true)} onMouseLeave={()=>setHot(false)} style={{transform:hot?'translateY(-2px)':''}} className={kind==='solid'?'solid-btn':'ghost-btn'} href={href}>{children}<span className="btn-arrow">↗</span></Link>}
export function SectionKicker({children}:{children:React.ReactNode}){return <div className="kicker"><span/>{children}</div>}
export function PageHero({kicker,title,lead,children}:{kicker:string,title:React.ReactNode,lead:string,children?:React.ReactNode}){return <section className="page-hero"><SectionKicker>{kicker}</SectionKicker><h1>{title}</h1><p>{lead}</p>{children}</section>}
