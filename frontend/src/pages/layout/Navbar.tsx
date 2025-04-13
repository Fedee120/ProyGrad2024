import { NavLink } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext"
import "./LayoutStyles.scss"
import Logo from '../../assets/logo.png'
import ProfilePopup from 'src/components/common/ProfilePopup/ProfilePopup'

const Navbar = () => {
    return (
        <div className="navbar-container">
            <div className="navigation-wrap">
                <img src={Logo} alt='logo' width={80} height={44}/>
                <NavLink to="/" className={({ isActive }) => isActive ? "navlink-item active" : "navlink-item"}>Chat</NavLink> 
                <NavLink to="/about" className={({ isActive }) => isActive ? "navlink-item active" : "navlink-item"}>Sobre el Proyecto</NavLink>
            </div>
            <div className="navbar-options">
                <ProfilePopup />
            </div>
        </div>
    )
}

export default Navbar