import { useState } from 'react'
import ContextMenu from '../ContextMenu/ContextMenu'
import './profilePopupStyles.scss'
import { User } from 'iconoir-react'
import { useAuth } from '../../../contexts/AuthContext'

const ProfilePopup = () => {
    const {logout} = useAuth()
    const [contextMenu, setContextMenu] = useState<{ x: number, y: number } | null>(null)

    const handleContextMenu = (event: React.MouseEvent) => {
        if(!contextMenu) {
            event.preventDefault()
            setContextMenu({ x: event.clientX, y: event.clientY })
        } else {
            handleCloseContextMenu()
        }
    }

    const handleCloseContextMenu = () => {
        setContextMenu(null)
    }

    const menuItems = [
        // { label: 'Profile', onClick: () => console.log('Profile clicked') },
        // { label: 'Settings', onClick: () => console.log('Settings clicked') },
        { label: 'Cerrar sesión', onClick: () => logout(), customClass: 'text-red-500 bg-red-50 hover:bg-red-100' }
    ]

    return (
        <div onClick={handleContextMenu} className="profile-popup">
            <div className="profile-icon"><User/></div>
            {contextMenu && (
                <ContextMenu items={menuItems} position={contextMenu} onClose={handleCloseContextMenu} user={true} />
            )}
        </div>
    )
}

export default ProfilePopup