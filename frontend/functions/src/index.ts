/**
 * Import function triggers from their respective submodules:
 *
 * import {onCall} from "firebase-functions/v2/https";
 * import {onDocumentWritten} from "firebase-functions/v2/firestore";
 *
 * See a full list of supported triggers at https://firebase.google.com/docs/functions
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();
import { calculateMissingPaymentsToDate, deletePendingPayments } from '../../src/services/firestoreServiceBackend'

const firestore = admin.firestore();

export const updateHistoryPayments = functions.pubsub.schedule('every 24 hours').onRun(async (context: any) => {
    const usersSnapshot = await firestore.collection('users').get()

    usersSnapshot.forEach(async (userDoc: any) => {
        const userData = userDoc.data()
        const properties = userData.properties || []

        for (const property of properties) {
            // Check expenses
            for (const expense of property.expenses || []) {
                await calculateMissingPaymentsToDate(userDoc.id, property.id, expense.id, 'expense')
            }

            // Check incomes
            for (const income of property.incomes || []) {
                await calculateMissingPaymentsToDate(userDoc.id, property.id, income.id, 'income')
            }
        }
    })
})

export const deleteAllPendingPayments = functions.https.onRequest(async (req: any, res: any) => {
    const usersSnapshot = await firestore.collection('users').get()

    usersSnapshot.forEach(async (userDoc: any) => {
        const userData = userDoc.data()
        const properties = userData.properties || []

        for (const property of properties) {
            // Check expenses
            for (const expense of property.expenses || []) {
                await deletePendingPayments(userDoc.id, property.id, expense.id, 'expense')
            }

            // Check incomes
            for (const income of property.incomes || []) {
                await deletePendingPayments(userDoc.id, property.id, income.id, 'income')
            }
        }
    })
    res.send('Pending payments deleted successfully')
})