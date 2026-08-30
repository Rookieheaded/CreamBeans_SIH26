import {Link} from 'react-router-dom'
import Icon from './Icon'
export default function ItemCard({item}){
 const date=item.timestamp?new Date(item.timestamp).toLocaleString([], {month:'short',day:'numeric',hour:'numeric',minute:'2-digit'}):'Date not provided'
 return <Link className="item-card" to={`/${item.type}/${item.id}`}>
  <div className="item-media">{item.image_url?<img src={item.image_url} alt=""/>:<div className="placeholder"><Icon name="image" size={34}/><span>No photo</span></div>}<span className={`status-pill ${item.status}`}>{item.status}</span></div>
  <div className="item-body"><div className="eyebrow">{item.type==='lost'?'LOST':'FOUND'} · {item.category||'OTHER'}</div><h3>{item.description}</h3><div className="item-meta"><span><Icon name="pin" size={15}/>{item.location||'Location not provided'}</span><span><Icon name="clock" size={15}/>{date}</span></div></div>
 </Link>
}
