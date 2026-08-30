import {useEffect,useMemo,useState} from 'react'
import {api} from '../api/client'
import ItemCard from './ItemCard'
import EmptyState from './EmptyState'
import Icon from './Icon'
export default function ItemListPage({type}){
 const [items,setItems]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState(''),[status,setStatus]=useState(''),[query,setQuery]=useState('')
 useEffect(()=>{let alive=true;setLoading(true);setError('');api.getItems({type,status:status||undefined,limit:100}).then(x=>{if(alive)setItems(x)}).catch(e=>{if(alive)setError(e.message)}).finally(()=>alive&&setLoading(false));return()=>{alive=false}},[type,status])
 const filtered=useMemo(()=>{const q=query.trim().toLowerCase();return q?items.filter(i=>[i.description,i.location,i.category].filter(Boolean).join(' ').toLowerCase().includes(q)):items},[items,query])
 return <section className="page container"><div className="page-head"><div><span className="kicker">CAMPUS INDEX</span><h1>{type==='lost'?'Lost items':'Found items'}</h1><p>{type==='lost'?'Search reports from students looking for something they lost.':'Browse items that students have found around campus.'}</p></div><div className="head-actions"><div className="search"><Icon name="search" size={18}/><input placeholder="Search this list" value={query} onChange={e=>setQuery(e.target.value)}/></div><select value={status} onChange={e=>setStatus(e.target.value)}><option value="">All statuses</option><option value="active">Active</option><option value="matched">Matched</option><option value="returned">Returned</option></select></div></div>
 {loading?<div className="grid">{[1,2,3,4,5,6].map(i=><div className="skeleton-card" key={i}/>)}</div>:error?<div className="error-state"><strong>Could not load items.</strong><span>{error}</span><button className="btn btn-primary" onClick={()=>location.reload()}>Retry</button></div>:filtered.length?<div className="grid">{filtered.map(i=><ItemCard key={i.id} item={i}/>)}</div>:<EmptyState title={query?'No matches found':'No reports yet'} text={query?'Try a different description, category, or location.':'Be the first person to add a report.'}/>}</section>
}
