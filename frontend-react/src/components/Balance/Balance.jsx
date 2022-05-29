import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import './style.scss';
import Loader from 'components/Loader/Loader';
import { update } from 'components/Redux/balance/actions';

const Balance = () => {
    const balance = useSelector((state) => state.balance.value);
    const dispatch = useDispatch();
    useEffect(() => dispatch(update()));

    return (
        <div className='balance'>
            <p style={{ fontWeight: 500, margin: 0 }}>Баланс</p>
            {balance ? <p style={{ margin: '5px 0 0' }}>{balance}</p> : <Loader />}
        </div>
    );
};
export default React.memo(Balance);
