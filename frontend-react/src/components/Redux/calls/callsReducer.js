import { UPDATE_CALLS } from './types';

const initialState = {
    list: undefined,
};

const callsReducer = (state = initialState, action) => {
    switch (action.type) {
        case UPDATE_CALLS:
            return { ...state, list: action.payload };
        default:
            return state;
    }
};
export default callsReducer;
