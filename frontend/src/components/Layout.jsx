import {Link,NavLink,useNavigate} from 'react-router-dom'
import {useAuth} from '../context/AuthContext'
import Icon from './Icon'
export default function Layout({children}){
 const {user,isAuthenticated,logout}=useAuth(); const navigate=useNavigate()
 return <div className="app-shell">
  <header className="topbar"><Link className="brand" to="/"><span className="bean-mark">●</span><span>Where Have You <em>Bean?</em></span></Link>
   <nav className="desktop-nav"><NavLink to="/lost">Lost items</NavLink><NavLink to="/found">Found items</NavLink>{isAuthenticated&&<NavLink to="/report">Report</NavLink>}</nav>
   <div className="nav-actions">{isAuthenticated?<><span className="user-chip"><Icon name="user" size={16}/>{user?.email}</span><button className="icon-btn" onClick={()=>{logout();navigate('/login')}} title="Sign out"><Icon name="logout"/></button></>:<Link className="btn btn-ghost" to="/login">Sign in</Link>}</div>
  </header><main>{children}</main><footer><div>© 2026 Where Have You Bean?</div><div>Campus lost & found · built for fast recovery</div></footer>
 </div>
}
