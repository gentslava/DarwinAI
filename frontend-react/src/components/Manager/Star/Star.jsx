import React from 'react';

const Star = ({ rating, color }) => (
    <div className='star'>
        <svg viewBox='0 0 45 44' fill='none' xmlns='http://www.w3.org/2000/svg'>
            <path
                d='M22.0531 1.00547C22.2376 0.637793 22.7624 0.637793 22.9469 1.00547L29.0603 13.1888C29.2717 13.6101 29.6688 13.9075 30.1325 13.9918L43.1195 16.3546C43.5075 16.4252 43.6649 16.8962 43.3972 17.1859L34.1532 27.1866C33.8489 27.5158 33.7078 27.9638 33.7686 28.408L35.6494 42.1593C35.7042 42.5606 35.2841 42.8572 34.9243 42.6712L23.1889 36.6039C22.7568 36.3805 22.2432 36.3805 21.8111 36.6039L10.0757 42.6712C9.71585 42.8572 9.29575 42.5606 9.35064 42.1593L11.2314 28.408C11.2922 27.9638 11.1511 27.5158 10.8468 27.1866L1.60281 17.1859C1.3351 16.8962 1.49245 16.4252 1.88049 16.3546L14.8675 13.9918C15.3312 13.9075 15.7283 13.6101 15.9397 13.1888L22.0531 1.00547Z'
                stroke={`url(#paint${color})`}
                fill={rating === '‒' ? '' : `url(#paint${color})`}
            />
            <defs>
                <linearGradient
                    id='paint0'
                    x1='22.5'
                    y1='-1'
                    x2='22.5'
                    y2='44'
                    gradientUnits='userSpaceOnUse'
                >
                    <stop stopColor='#6100FF' />
                    <stop offset='1' stopColor='#03DAC5' />
                </linearGradient>
                <linearGradient
                    id='paint1'
                    x1='22.5'
                    y1='-1'
                    x2='22.5'
                    y2='44'
                    gradientUnits='userSpaceOnUse'
                >
                    <stop stopColor='#6100FF' />
                    <stop offset='1' stopColor='#DBB2FF' />
                </linearGradient>
                <linearGradient
                    id='paint2'
                    x1='22.5'
                    y1='-1'
                    x2='22.5'
                    y2='44'
                    gradientUnits='userSpaceOnUse'
                >
                    <stop stopColor='#B00020' />
                    <stop offset='1' stopColor='#FF002E' />
                </linearGradient>
            </defs>
        </svg>
        <span style={rating === '‒' ? { color: '#707070' } : {}}>{rating}</span>
    </div>
);
export default React.memo(Star);
