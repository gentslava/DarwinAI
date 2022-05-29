import Loader from 'components/Loader/Loader';
import React from 'react';
import { Link } from 'react-router-dom';
import './style.scss';

const style = {
    display: 'block',
    marginTop: '-50px',
    marginBottom: '30px',
};

const Table = ({ name, headers, calls, className }) => (
    <div className={`table ${className}`}>
        <span style={style}>{name}</span>
        <div className='tr table-headers'>
            {headers.map((header, i) => (
                <span className='th' key={i}>
                    {header}
                    <span className='icon-Down' />
                </span>
            ))}
        </div>
        {calls
            ? calls.map((call, i) => (
                <Link
                    to={call.path}
                    target='_blank'
                    rel='noreferrer'
                    className='tr'
                    rowid={call.id}
                    key={i}
                >
                    {call.data.map((data, j) => (
                        <span className='td' key={j}>
                            {data}
                        </span>
                    ))}
                </Link>
            ))
            : <Loader />}
    </div>
);
export default React.memo(Table);
