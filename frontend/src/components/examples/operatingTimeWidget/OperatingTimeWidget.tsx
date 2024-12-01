import React, { useState } from 'react';
import './OperatingTimeWidgetStyles.scss';

const daysOfWeek = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'];
const timeSlotsAM = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
const timeSlotsPM = ['13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24'];

export const OperatingTimeWidget = () => {
    const [selectedDay, setSelectedDay] = useState<string>('Lun');
    const [selectedSlots, setSelectedSlots] = useState<{ [key: string]: string[] }>({});

    const toggleSlot = (day: string, slot: string) => {
        setSelectedSlots(prev => {
            const daySlots = prev[day] || [];
            if (daySlots.includes(slot)) {
                return { ...prev, [day]: daySlots.filter(s => s !== slot) };
            } else {
                return { ...prev, [day]: [...daySlots, slot] };
            }
        });
    };

    const getDayClass = (day: string) => {
        const baseClass = 'day-name'
        const activeClass = selectedSlots[day]?.length > 0 ? 'active' : 'inactive'
        const selectedClass = day === selectedDay ? 'selected' : ''
        return `${baseClass} ${activeClass} ${selectedClass}`.trim()
    }

    return (
        <div className="operating-time-widget">
            <div className="header">
                <div className="title">Horario de operación</div>
            </div>
            <div className="days">
                {daysOfWeek.map(day => (
                    <div key={day} className={getDayClass(day)} onClick={() => setSelectedDay(day)}>
                        {day}
                    </div>
                ))}
            </div>
            <div className="time-slots">
                <div className="am">
                    <div className="label">AM</div>
                    <div className="time-slots-container">
                        {timeSlotsAM.map(slot => (
                            <div key={slot} className={`time-slot ${selectedSlots[selectedDay]?.includes(slot) ? 'selected' : ''}`} onClick={() => toggleSlot(selectedDay, slot)}>{slot}</div>
                        ))}
                    </div>
                </div>
                <div className="pm">
                    <div className="label">PM</div>
                    <div className="time-slots-container">
                        {timeSlotsPM.map(slot => (
                            <div key={slot} className={`time-slot ${selectedSlots[selectedDay]?.includes(slot) ? 'selected' : ''}`} onClick={() => toggleSlot(selectedDay, slot)}>
                                {slot}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}