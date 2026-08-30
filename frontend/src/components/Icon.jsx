export default function Icon({name,size=20}){
 const p={width:size,height:size,viewBox:'0 0 24 24',fill:'none',stroke:'currentColor',strokeWidth:'1.8',strokeLinecap:'round',strokeLinejoin:'round'}
 const paths={
  search:<><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  plus:<><path d="M12 5v14M5 12h14"/></>,
  pin:<><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
  clock:<><circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3 2"/></>,
  arrow:<><path d="M5 12h13"/><path d="m13 6 6 6-6 6"/></>,
  check:<><path d="m5 12 4 4L19 6"/></>,
  shield:<><path d="M12 3 19 6v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3Z"/><path d="m9 12 2 2 4-4"/></>,
  menu:<><path d="M4 7h16M4 12h16M4 17h16"/></>,
  user:<><circle cx="12" cy="8" r="3.2"/><path d="M5 20c.8-3.2 3.1-5 7-5s6.2 1.8 7 5"/></>,
  image:<><rect x="4" y="4" width="16" height="16" rx="2"/><circle cx="9" cy="9" r="1.5"/><path d="m20 15-4-4L7 20"/></>,
  chevron:<path d="m8 10 4 4 4-4"/>,
  logout:<><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M21 19V5a2 2 0 0 0-2-2h-5"/></>,
 }
 return <svg {...p}>{paths[name]||paths.search}</svg>
}
