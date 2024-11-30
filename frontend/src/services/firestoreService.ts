import {
  getDoc,
  doc,
  setDoc,
  updateDoc,
  collection,
  getDocs,
  deleteDoc,
} from "firebase/firestore";
import { firestoreDB } from "../firebase";
// import { User } from "../types/user";

// export const getUserDocument = async (userId: string) => {
//   const docRef = doc(firestoreDB, "users", userId);
//   const docSnap = await getDoc(docRef);
//   if (docSnap.exists()) {
//     return { ...docSnap.data(), id: userId } as User;
//   } else {
//     return null;
//   }
// };
