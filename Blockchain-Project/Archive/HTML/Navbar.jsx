import styles from "./navbar.module.css";
import { useState } from "react";
import sidelogo from "../../assets/sidebarlogo.png";
import dinoinstagram from "../../assets/dinoinstagram.png";
import euiruminstagram from "../../assets/euiruminstagram.png";
import menu from "../../assets/menu.png";
import header from "../../assets/headertext.png";
import navline from "../../assets/navline.png";
import styled from "styled-components";
const navbar = styled.div`
  max-width: 500px;
  width: 100%;
  height: var(--navbar-height);
  background-color: #f89cc5;
  position: fixed;
  overflow-x: clip;
  z-index: 9999;
`;
const headerflex = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const view_detail = styled.button`
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  border: none;
  outline: none;
  background: none;
`;

const headeflex2 = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
`;

const headerimg = styled.img``;
const sidemenuimg = styled.img``;

const sidemenu = styled.div``;

const sidemenuline = styled.div``;

const titleimgfleximg = styled.div``;
const sideflextextscope = styled.div``;

const story_detail = styled.div``;
const test_detail = styled.div``;
const diary_detail = styled.div``;

const Navbar = () => {
  const [isSideMenuActive, setSideMenuActive] = useState(false);
  return (
    <navbar className={styles.navbar}>
      {" "}
      <headerflex className={styles.headerflex}>
        <view_detail
          className={styles.view_detail}
          onClick={() => setSideMenuActive(!isSideMenuActive)}
          id="view"
        >
          <sidemenuimg
            src={menu}
            className={styles.sidemenuimg}
            alt="menuimg"
          />
        </view_detail>{" "}
      </headerflex>{" "}
      <a href="/">
        <headeflex2 className={styles.headeflex2}>
          <headerimg src={header} className={styles.headerimg} alt="menuimg" />
        </headeflex2>
      </a>
      <sidemenu
        className={
          styles.sidemenu + (isSideMenuActive ? styles.sidemenu.active : "")
        }
      >
        <sidemenuline className={styles.sidemenuline}>
          {" "}
          <a href="/" className={styles.activea}>
            {" "}
            <titleimgfleximg className={styles.titleimgfleximg}>
              <img src={sidelogo} alt="sidelogo" className={styles.sidelogo} />
            </titleimgfleximg>
          </a>
          <sideflextextscope className={styles.sideflextextscope}>
            <a href="/story" className={styles.activea} type="s">
              <story_detail className={styles.story_detail}>
                <p id="story_detail">디노스토리</p>
                {/* <img src={dinostory} alt="디노스토리" className="dinostory" /> */}
              </story_detail>
            </a>{" "}
            <a href="/test" className={styles.activea} type="s">
              <test_detail className={styles.test_detail}>
                <img src={navline} className={styles.headline} />
                <p id="test_detail">백수 삶의 현장</p>{" "}
                {/* <img src={title2} alt="백수삶의현장" className="twonav" /> */}
              </test_detail>
            </a>
            <a href="/write" className={styles.activea} type="s">
              <diary_detail className={styles.diary_detail}>
                {" "}
                <img src={navline} className={styles.headline} />{" "}
                <p id="diary_detail">백수의 일기장</p>
                {/* <img src={treenav} alt="백수의일기장" className="treenav" /> */}
              </diary_detail>
            </a>{" "}
            <a href="/game" className={styles.activea} type="s">
              <div className={styles.diary_detail}>
                {" "}
                <img src={navline} className={styles.headline} />{" "}
                <p id="diary_game">백런스 게임</p>
                {/* <img src={treenav} alt="백수의일기장" className="treenav" /> */}
              </div>
            </a>{" "}
            <a href="/endstory" className={styles.activea} type="s">
              <div className={styles.endstory_detail}>
                {" "}
                <img src={navline} className={styles.headline} />{" "}
                <p id={"mascot_dino"}>마스코트 디노</p>
                {/* <img src={treenav} alt="백수의일기장" className="treenav" /> */}
              </div>
            </a>
          </sideflextextscope>{" "}
          <div className={styles.instagram_layout}>
            <div className={styles.sideinstagramscope} id="dino_insta">
              {" "}
              <a
                href="https://www.instagram.com/1dang100_dino"
                className={styles.activea}
                type="s"
                target="_blank"
              >
                <img
                  src={dinoinstagram}
                  alt="dinoinstagram"
                  className={styles.dino_insta}
                />
              </a>
            </div>
            <div className={styles.sideinstagramscope} id="youthroom_insta">
              <a
                href={"https://instagram.com/youtheroom?igshid=YmMyMTA2M2Y="}
                className={styles.activea}
                type="s"
                target="_blank"
              >
                <img
                  src={euiruminstagram}
                  className={styles.youtheroom_insta}
                  alt="dinoinstagram"
                />
              </a>
            </div>
          </div>{" "}
        </sidemenuline>{" "}
      </sidemenu>
    </navbar>
  );
};

export default Navbar;
