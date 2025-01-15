import React, { useRef, useEffect } from 'react'
import './contextMenuStyles.scss'
import { useAuth } from '../../../contexts/AuthContext'

interface ContextMenuProps {
    items: { label: string, onClick: () => void , customClass?: string}[]
    position: { x: number, y: number }
    onClose: () => void
    user: boolean
}

const ContextMenu: React.FC<ContextMenuProps> = ({ items, position, onClose, user = false }) => {
    const menuRef = useRef<HTMLDivElement>(null)
    const {currentUser} = useAuth()


    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                onClose()
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [onClose])

    const handleItemClick = (onClick: () => void) => {
        onClick()
        onClose()
    }

    return (
        <div className="context-menu" style={{ top: position.y, left: position.x - 200 }} ref={menuRef} onClick={(e) => e.stopPropagation()}>
            {user && (
                <div className="text-[14px] text-[#404040] py-2 px-3">
                    {currentUser.firstName} {currentUser.lastName}
                    <div className="text-[12px] text-[#606060]">{currentUser.email}</div>
                </div>
            )}
            {items.map((item, index) => (
                <div 
                    key={index} 
                    className={`py-2 px-4 cursor-pointer w-[200px] hover:bg-gray-100 ${item.customClass}`} 
                    onClick={() => handleItemClick(item.onClick)}
                >
                    {item.label}
                </div>
            ))}
        </div>
    )
}

export default ContextMenu
