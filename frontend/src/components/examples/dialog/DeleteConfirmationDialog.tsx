import { useState, useEffect } from 'react'
import Button from '../../common/Button/Button'
import { Xmark } from 'iconoir-react'
import './dialogStyles.scss'

const DeleteConfirmationDialog = ({ isOpen, close, onDelete, loading, title = "Delete", message = "Are you sure you want to proceed? this action cannot be rolled back" }: { isOpen: boolean, close: () => void, onDelete: () => void, loading: boolean, title?: string, message?: string }) => {
    const [isConfirmEnabled, setIsConfirmEnabled] = useState(false)
    const [timer, setTimer] = useState(5)

    useEffect(() => {
        if (isOpen) {
            setIsConfirmEnabled(false)
            setTimer(5)
            const countdown = setInterval(() => {
                setTimer(prev => {
                    if (prev <= 1) {
                        clearInterval(countdown)
                        setIsConfirmEnabled(true)
                        return 0
                    }
                    return prev - 1
                })
            }, 1000)
            return () => clearInterval(countdown)
        }
    }, [isOpen])

    return (
        isOpen ? (
            <div className="overlay">
                <div className="dialog-container">
                    <div className="header">
                        <div className="header-title">{title}</div>
                        <div className="icon-box-close" onClick={close}>
                            <Xmark color="#404040"/>
                        </div>
                    </div>
                    <div className="form-container mt-4">
                        <div className='label mb-1 text-[14px] text-[#404040]'>{message}</div>
                    </div>
                    <div className="flex w-full justify-end gap-2">
                        <Button variant='secondary' onClick={close}>Cancel</Button>
                        <Button variant='danger' onClick={onDelete} disabled={!isConfirmEnabled || loading}>
                            Delete{!!timer && ` (${timer}s)`}
                        </Button>
                    </div>
                </div>
            </div>
        ) : null
    )
}

export default DeleteConfirmationDialog