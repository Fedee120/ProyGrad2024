const UYU_TO_USD_CONVERSION_RATE = 40

const convertToUSD = (amount: number, currency: string) => {
    return currency === 'USD' ? amount : amount / UYU_TO_USD_CONVERSION_RATE
}

const calculateAnnualizedAmount = (amount: number, frequency: string) => {
    switch (frequency) {
        case 'Monthly':
            return amount * 12
        case 'Quarterly':
            return amount * 4
        case 'Four-Month Period':
            return amount * 3
        case 'Semestral':
            return amount * 2
        case 'Yearly':
            return amount
        default:
            return amount
    }
}


export function formatDate(dateString: string): string {
    const date = new Date(dateString)
    const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short', year: 'numeric' }
    return date.toLocaleDateString('en-GB', options).replace(/ /g, ' ')
}